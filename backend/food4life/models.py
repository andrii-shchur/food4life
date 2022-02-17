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
    description = models.CharField(max_length=5000)
    name = models.CharField(max_length=100, unique=True)
    img_path = models.CharField(max_length=255, null=True)
    calories = models.CharField(max_length=50, null=True)
    proteins = models.CharField(max_length=50, null=True)
    fats = models.CharField(max_length=50, null=True)
    carbs = models.CharField(max_length=50, null=True)
    yields = models.CharField(max_length=50, null=True)
    time = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], default=2)
    # est_time в хвилинах
    est_time = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(300)])

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, default='NoNameProduct')

    def __str__(self):
        return f'recipe_id:{self.recipe} amount:{self.description}'


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = (('user', 'recipe'),)

    def __str__(self):
        return f'user:{self.user} recipe:{self.recipe} rating:{self.rating}'


class Favourites(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'user_id:{self.user} recipe_id:{self.recipe}'
