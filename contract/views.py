import random

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ApiProfile
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.http import JsonResponse
import json
import ipfshttpclient
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect
from .forms import LayerFolderForm
from .models import LayerFolder, GeneratedImage
from django.contrib.auth.decorators import login_required

from django.core.files.base import ContentFile
from .utils import generate_image_from_zip
import os
from io import BytesIO
from django.contrib.auth import logout


def logout_view(request):
    logout(request)

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



def save_account(request):
    data = json.loads(request.body)
    eth_address = data.get('account')
    profile, created = ApiProfile.objects.get_or_create(user=request.user)
    profile.eth_address = eth_address
    profile.save()

    return JsonResponse({"success": "Ethereum address saved successfully."})


def home(request):
    images = GeneratedImage.objects.filter()[:8]
    return render(request, 'images/index.html', {'images': images})


@login_required
def list_folders(request):
    folders = LayerFolder.objects.filter(user=request.user)
    return render(request, 'images/folder.html', {'folders': folders})

@login_required
def list_folders_details(request, id):
    folder = get_object_or_404(LayerFolder, user=request.user, pk=id)
    images = folder.generated_images.all()
    return render(request, 'images/list_images.html', {'folder': folder, 'images': images})


@login_required
def generate_images_view(request):
    if request.method == 'POST':
        form = LayerFolderForm(request.POST, user=request.user)
        if form.is_valid():
            layer_folder = form.cleaned_data['layer_folder']
            folder_path = layer_folder.folder.path

            generated_images = []
            # Connect to IPFS
            with ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001') as client:
                for i in range(100):
                    generated_image = generate_image_from_zip(folder_path)
                    if generated_image:
                        image_io = BytesIO()
                        generated_image.save(image_io, format='PNG')
                        filename = f'generated_image_{layer_folder.id}_{i+1}.png'

                        new_image = GeneratedImage(layer_folder=layer_folder, user=request.user)
                        new_image.image.save(filename, ContentFile(image_io.getvalue()))
                        new_image.save()
                        generated_images.append(new_image)

                        # Upload to IPFS
                        image_path = new_image.image.path
                        ipfs_result = client.add(image_path)
                        new_image.ipfs_hash = ipfs_result['Hash']
                        new_image.save()

            if generated_images:
                random_image = random.choice(generated_images)
                layer_folder.image = random_image.image
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
        LayerFolder.objects.create(user=request.user, folder=my_file, name=my_file.name)
        return redirect('list_folders')

    return JsonResponse({"post": "false"})


