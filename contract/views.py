import requests

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

from .forms import SignUpForm, EmailAuthenticationForm

import json
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from web3 import Web3
from web3.middleware import geth_poa_middleware
from .models import LayerFolder, GeneratedImage, ApiProfile
from .forms import LayerFolderForm
from .utils import generate_image_from_zip
import os
from dotenv import load_dotenv

load_dotenv()


def save_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            eth_address = data.get('account')
            if not eth_address:
                return JsonResponse({"error": "Ethereum address is required."}, status=400)

            # Check if the eth_address already has an ApiProfile
            try:
                profile = ApiProfile.objects.get(eth_address=eth_address)
                login(request, profile.user)
                return JsonResponse({"success": "Logged in successfully."})
            except ApiProfile.DoesNotExist:
                pass

            # Check if the current user is authenticated and create an ApiProfile if it does not exist
            if request.user.is_authenticated:
                profile, created = ApiProfile.objects.get_or_create(user=request.user, defaults={'eth_address': eth_address})
                if created:
                    return JsonResponse({"success": "ApiProfile created successfully."})
                else:
                    return JsonResponse({"error": "ApiProfile already exists for this user."}, status=400)
            else:
                return JsonResponse({"error": "User is not authenticated."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)




def mint_nft(request, pk):
    try:
        image = GeneratedImage.objects.get(pk=pk)
        infura_url = os.getenv('INFURA_PROJECT_URL')
        contract_address = os.getenv('CONTRACT_ADDRESS')
        private_key = os.getenv('PRIVATE_KEY')

        web3 = Web3(Web3.HTTPProvider(infura_url))

        app_dir = os.path.dirname(os.path.abspath(__file__))
        abi_path = os.path.join(app_dir, 'contract_abi.json')
        with open(abi_path) as f:
            contract_abi = json.load(f)
        address = os.getenv('ADDRESS')
        user_address = address

        contract = web3.eth.contract(address=contract_address, abi=contract_abi)

        ipfs_hash = image.token_uri
        if not ipfs_hash:
            return JsonResponse({'error': 'IPFS hash is required'}, status=400)

        transaction = contract.functions.createCollectable(str(ipfs_hash))


        tx = transaction.build_transaction({
            'chainId': 11155111,
            'gas': 1000000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(user_address),
        })
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        image.tx_hash = tx_hash.hex()
        image.save(update_fields=['tx_hash'])
        return JsonResponse({'transaction_hash': web3.to_hex(tx_hash)})

    except Exception as e:
        print(f"Error minting NFT: {e}")
        return JsonResponse({'error': 'Could not mint NFT'}, status=500)

@login_required
def like_image(request, image_id):
    image = get_object_or_404(GeneratedImage, id=image_id)
    if image.likes.filter(id=request.user.id).exists():
        image.likes.remove(request.user)
        liked = False
    else:
        image.likes.add(request.user)
        image.dislikes.remove(request.user)
        liked = True
    return JsonResponse({'total_likes': image.total_likes(), 'liked': liked, 'total_dislikes': image.total_dislikes()})

@login_required
def dislike_image(request, image_id):
    image = get_object_or_404(GeneratedImage, id=image_id)
    if image.dislikes.filter(id=request.user.id).exists():
        image.dislikes.remove(request.user)
        disliked = False
    else:
        image.dislikes.add(request.user)
        image.likes.remove(request.user)
        disliked = True
    return JsonResponse({'total_dislikes': image.total_dislikes(), 'disliked': disliked, 'total_likes': image.total_likes()})

PINATA_JWT = os.getenv('PINATA_JWT')

def upload_to_pinata(file_obj):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        'Authorization': f'Bearer {PINATA_JWT}'
    }
    files = {'file': (file_obj)}
    response = requests.post(url, files=files, headers=headers)
    response.raise_for_status()
    ipfs_hash = response.json()['IpfsHash']
    return ipfs_hash

@login_required
def generate_and_mint_nfts(request):
    if request.method == 'POST':
        form = LayerFolderForm(request.POST, user=request.user)
        if form.is_valid():
            layer_folder = form.cleaned_data['layer_folder']
            folder_path = layer_folder.folder.path

            metadata_hashes = []

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
                        image_io.seek(0)

                        ipfs_image_hash = upload_to_pinata(image_io)

                        metadata = {
                            "name": f"Generated Image #{i + 1}",
                            "description": "An image generated from the layer folder",
                            "image": f"ipfs://{ipfs_image_hash}"
                        }
                        metadata_io = BytesIO(json.dumps(metadata).encode())
                        ipfs_metadata_hash = upload_to_pinata(metadata_io)
                        metadata_hashes.append(ipfs_metadata_hash)

                        # Save the image and metadata info to the database
                        GeneratedImage.objects.create(
                            layer_folder=layer_folder,
                            user=request.user,
                            ipfs_hash=ipfs_image_hash,
                            token_uri=f"ipfs://{ipfs_metadata_hash}",
                        )

                    except IOError as e:
                        print(f"Failed to process or upload image: {e}")
                        continue

            return JsonResponse({'metadata_hashes': metadata_hashes})

        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = LayerFolderForm(user=request.user)
    return render(request, 'images/generate_images.html', {'form': form})


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
    folder = get_object_or_404(LayerFolder, pk=pk)
    images = folder.generated_images.all()
    return render(request, 'images/list_images.html', {'folder': folder, 'images': images})


class CreatingFolderView(LoginRequiredMixin, TemplateView):
    template_name = 'images/create_folder.html'


@login_required
def create_folder(request):
    if request.method == 'POST':
        my_file = request.FILES.get("file")
        if not my_file:
            return JsonResponse({"error": "No file provided"}, status=400)

        folder = LayerFolder.objects.create(user=request.user, folder=my_file, name=my_file.name)

        try:
            folder_path = folder.folder.path
            generated_image = generate_image_from_zip(folder_path)

            image_io = BytesIO()
            generated_image.save(image_io, format='PNG')
            image_io.seek(0)

            ipfs_image_hash = upload_to_pinata(image_io)
            folder.ipfs_hash = ipfs_image_hash
            folder.save()
        except Exception as e:
            folder.delete()  # Clean up if there was an error
            return JsonResponse({"error": str(e)}, status=500)

        return redirect('list_folders')

    return JsonResponse({"post": "false"})


def get_contract_data(request):
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        abi_path = os.path.join(app_dir, 'contract_abi.json')
        with open(abi_path) as f:
            contract_abi = json.load(f)
        contract_address = "0xf808Fc7c5483Da441eC5965648153642414cF898"

        if not contract_address:
            return JsonResponse({'error': 'Contract address not found'}, status=500)

        return JsonResponse({
            'abi': contract_abi,
            'address': contract_address
        })

    except Exception as e:
        print(f"Error loading contract data: {e}")
        return JsonResponse({'error': 'Could not load contract data'}, status=500)

def delete_folder(request, folder_id):
    folder = get_object_or_404(LayerFolder, pk=folder_id)
    folder.delete()
    messages.success(request, "The LayerFolder has been deleted")
    return redirect("list_folders")

def delete_image(request, image_id):
    image = get_object_or_404(GeneratedImage, pk=image_id)
    print(image)
    image.delete()
    messages.success(request, "The image has been deleted")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
def update_image(request, image_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Parsed JSON data:", data)

            tx_hash = data.get('tx_hash')
            owner_address = data.get('owner_address')
            token_id = data.get('token_id')
            price_ether = data.get('price')

            print(f"Updating image with id: {image_id}")
            image = GeneratedImage.objects.get(id=image_id)
            image.tx_hash = tx_hash
            image.user = request.user
            image.owner_address = owner_address
            image.price = price_ether
            print(price_ether)
            if token_id:
                image.token_id = token_id

            image.save()
            return JsonResponse({'status': 'success'})
        except GeneratedImage.DoesNotExist:
            print("Error: Image not found")
            return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def profile(request):
    profile = ApiProfile.objects.get(user=request.user)
    bought = GeneratedImage.objects.filter(user=request.user, tx_hash__isnull=False).count()
    sell = GeneratedImage.objects.exclude(user=request.user).filter(tx_hash__isnull=False).count()

    filter_images = request.GET.get('filter_image', "bought")
    print(filter_images)

    if filter_images == "sale":
        images = GeneratedImage.objects.exclude(user=request.user).filter(tx_hash__isnull=False)
        name = "On Sale"
    else:
        images = GeneratedImage.objects.filter(user=request.user, tx_hash__isnull=False)
        name = "Owned NFT"
    print(images)
    return render(request, 'registration/profile.html', {'profile': profile,
                                                         "bought": bought,
                                                         "sell": sell,
                                                         "images": images,
                                                         "filter_name": name})


def about_us(request):
    return render(request, "about_us.html")

def facts(request):
    return render(request, "facts.html")