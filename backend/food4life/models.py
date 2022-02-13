from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have email')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f'user:{self.user} recipe_id:{self.recipe_id} rating:{self.rating}'
