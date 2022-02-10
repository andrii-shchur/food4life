from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# напевно юзлесна модель, будем юзати django.contrib.auth.models.User
class User(models.Model):
    fname = models.CharField(max_length=64)
    lname = models.CharField(max_length=64)
    email = models.EmailField()
    password = models.BinaryField(max_length=60)

    def __str__(self):
        return f'{self.fname} {self.lname} {self.email}'


class Recipe(models.Model):
    difficulty = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.CharField(max_length=500)
    name = models.CharField(max_length=100, unique=True)
    type = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    img_path = models.CharField(max_length=255, unique=True)
    # тут est_time в хвилинах
    est_time = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(300)])

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    img_path = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    proteins = models.DecimalField(max_digits=10, decimal_places=2)
    fats = models.DecimalField(max_digits=10, decimal_places=2)
    carbs = models.DecimalField(max_digits=10, decimal_places=2)
    # хз який валідатор для measure_type
    measure_type = models.IntegerField()

    def __str__(self):
        return f'{self.name} {self.price}'


class Category(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.product_id} {self.alias}'


class Ingredient(models.Model):
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'recipe_id:{self.recipe_id} product_id:{self.product_id} amount:{self.amount}'


class Rating(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f'user_id:{self.user_id} recipe_id:{self.recipe_id} rating:{self.rating}'
