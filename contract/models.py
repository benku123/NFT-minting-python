# models.py
from django.db import models
from django.contrib.auth.models import User

class ApiProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name="api_profile")
    eth_address = models.CharField(max_length=42)
    profile_image = models.ImageField(upload_to='profile_images/', default='image/user.png', null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username if self.user else "No User"

class LayerFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.FileField(upload_to='layer_folders/')
    name = models.CharField(max_length=100, null=True, blank=True)
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s layer folder: {self.name}"

class GeneratedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    layer_folder = models.ForeignKey(LayerFolder, related_name='generated_images', on_delete=models.CASCADE)
    token_id = models.CharField(max_length=255, blank=True, null=True)
    token_uri = models.CharField(max_length=255, blank=True, null=True)
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_images', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_images', blank=True)
    tx_hash = models.CharField(max_length=500, blank=True, null=True)
    owner_address = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=36, decimal_places=3, default=0.001)

    def __str__(self):
        return f"Image {self.id} from {self.layer_folder}"

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    class Meta:
        verbose_name = 'Generated Image'
        verbose_name_plural = 'Generated Images'