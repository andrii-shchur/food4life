# Generated by Django 4.0.1 on 2022-02-22 18:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food4life', '0007_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='calories',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10000)]),
        ),
    ]
