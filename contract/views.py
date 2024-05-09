import requests
import json
from io import BytesIO

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import ApiProfile
from .forms import SignUpForm, EmailAuthenticationForm
from .forms import LayerFolderForm
from .models import LayerFolder, GeneratedImage
from .utils import generate_image_from_zip

def logout_view(request):
    logout(request)
    return redirect('home')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def email_login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
        else:
            pass
    else:
        form = EmailAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

def save_account(request):
    data = json.loads(request.body)
    eth_address = data.get('account')
    profile, created = ApiProfile.objects.get_or_create(user=request.user)
    print(profile, created)
    profile.eth_address = eth_address
    profile.save()

    return JsonResponse({"success": "Ethereum address saved successfully."})


def home(request):
    images = GeneratedImage.objects.filter()[:8]
    return render(request, 'images/index.html', {'images': images})



def list_folders(request):
    folders = LayerFolder.objects.all()
    return render(request, 'images/folder.html', {'folders': folders})

@login_required
def personal_list_folder(request):
    folders = LayerFolder.objects.filter(user=request.user)
    return render(request, 'images/folder.html', {'folders': folders})


@login_required
def list_folders_details(request, pk):
    folder = get_object_or_404(LayerFolder, user=request.user, pk=pk)
    images = folder.generated_images.all()
    return render(request, 'images/list_images.html', {'folder': folder, 'images': images})


@login_required
def generate_images_view(request):
    if request.method == 'POST':
        form = LayerFolderForm(request.POST, user=request.user)
        if form.is_valid():
            layer_folder = form.cleaned_data['layer_folder']
            folder_path = layer_folder.folder.path

            first_image_hash = None
            for i in range(20):
                generated_image = generate_image_from_zip(folder_path)
                if generated_image:
                    try:
                        generated_image.verify()
                    except Exception as e:
                        print(f"Image verification failed: {e}")
                        continue

                    image_io = BytesIO()
                    try:
                        generated_image.save(image_io, format='PNG')
                        image_io.seek(0)  # Rewind the buffer

                        files = {'file': ('image.png', image_io, 'image/png')}
                        response = requests.post('http://127.0.0.1:5001/api/v0/add', files=files)
                        response.raise_for_status()  # Check for HTTP errors
                        ipfs_result = response.json()
                        ipfs_hash = ipfs_result['Hash']

                        GeneratedImage.objects.create(
                            layer_folder=layer_folder,
                            user=request.user,
                            ipfs_hash=ipfs_hash
                        )

                        if i == 0:
                            first_image_hash = ipfs_hash
                    except IOError as e:
                        print(f"Failed to process or upload image: {e}")
                        continue
            if first_image_hash:
                layer_folder.ipfs_image_hash = first_image_hash
                layer_folder.save()

            return redirect('home')
        else:
            print(form.errors)
    else:
        form = LayerFolderForm(user=request.user)
    return render(request, 'images/generate_images.html', {'form': form})

class CreatingFolderView(LoginRequiredMixin, TemplateView):
    template_name = 'images/create_folder.html'

@login_required
def create_folder(request):
    if request.method == 'POST':
        my_file = request.FILES.get("file")
        folder = LayerFolder.objects.create(user=request.user, folder=my_file, name=my_file.name)
        folder_path = folder.folder.path
        generated_image = generate_image_from_zip(folder_path)

        image_io = BytesIO()

        generated_image.save(image_io, format='PNG')
        image_io.seek(0)

        files = {'file': ('image.png', image_io, 'image/png')}
        response = requests.post('http://127.0.0.1:5001/api/v0/add', files=files)
        response.raise_for_status()
        ipfs_result = response.json()
        ipfs_hash = ipfs_result['Hash']
        folder.ipfs_image_hash = ipfs_hash
        folder.save()
        return redirect('list_folders')

    return JsonResponse({"post": "false"})


