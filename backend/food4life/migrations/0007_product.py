# Generated by Django 4.0.1 on 2022-02-22 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food4life', '0006_alter_recipe_est_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Default Product', max_length=250)),
                ('img_path', models.CharField(max_length=255, null=True)),
                ('calories', models.CharField(max_length=50, null=True)),
                ('proteins', models.CharField(max_length=50, null=True)),
                ('fats', models.CharField(max_length=50, null=True)),
                ('carbs', models.CharField(max_length=50, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('category', models.CharField(max_length=250, null=True)),
            ],
        ),
    ]
