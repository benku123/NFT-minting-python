from django.http import HttpResponse
from .models import ApiProfile
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

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

    # Get or create a UserCryptoProfile instance for the user
    profile, created = ApiProfile.objects.get_or_create(user=request.user)
    profile.eth_address = eth_address
    profile.save()

    return JsonResponse({"success": "Ethereum address saved successfully."})

def home(request):
    return HttpResponse("Hello, world. You're at the")
