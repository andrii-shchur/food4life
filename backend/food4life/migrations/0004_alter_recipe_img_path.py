# Generated by Django 4.0.1 on 2022-02-13 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food4life', '0003_rename_recipe_id_ingredient_recipe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='img_path',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
