# Generated by Django 4.2 on 2024-06-13 07:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contract', '0024_alter_apiprofile_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apiprofile',
            name='user',
        ),
        migrations.AddField(
            model_name='apiprofile',
            name='api_profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
