# Generated by Django 5.0.3 on 2024-06-04 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contract", "0017_alter_generatedimage_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generatedimage",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=3, max_digits=36, null=True
            ),
        ),
    ]
