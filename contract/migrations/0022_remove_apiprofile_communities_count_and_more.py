# Generated by Django 5.0.3 on 2024-06-04 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("contract", "0021_apiprofile_communities_count_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="apiprofile",
            name="communities_count",
        ),
        migrations.RemoveField(
            model_name="apiprofile",
            name="discussions_count",
        ),
        migrations.RemoveField(
            model_name="apiprofile",
            name="reviews_count",
        ),
    ]
