# Generated by Django 4.0.1 on 2022-02-17 21:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food4life', '0005_alter_categories_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='est_time',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(300)]),
        ),
    ]
