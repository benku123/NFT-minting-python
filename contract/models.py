# models.py
from django.db import models
from django.contrib.auth.models import User

class ApiProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    eth_address = models.CharField(max_length=42) # Ethereum addresses are 42 characters long

