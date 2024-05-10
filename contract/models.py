# models.py
from django.db import models
from django.contrib.auth.models import User

class ApiProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    eth_address = models.CharField(max_length=42) # Ethereum addresses are 42 characters long




class LayerFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.FileField(upload_to='layer_folders/')
    name = models.CharField(max_length=100, null=True, blank=True)
    ipfs_image_hash = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s layer folder: {self.name}"

class GeneratedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    layer_folder = models.ForeignKey(LayerFolder, related_name='generated_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='generated_images/')
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image {self.id} from {self.layer_folder}"

