import json
import random

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *
from .models import *
from .forms import *


from .object_detection.detect import predict
from django.db.models import Avg
from django.db.utils import IntegrityError

from .filtermanager import FilterManager


@api_view(['POST'])
@permission_classes([])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.data)
        if form.is_valid():
            form.save()
            return Response({'email': form.cleaned_data['email']}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def log_out(request):
    if request.method == 'POST':
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_prediction(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = predict(request.FILES['file'])
            return Response(result, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def recommend(request):
    if request.method == 'GET':
        products = request.data['list']
        # ахтунг костиль
        result = set(range(1, 10000))
        for product in products:
            q = Ingredient.objects.filter(description__icontains=product).values()
            ids = set()
            for el in q:
                ids.add(el['recipe_id'])
            result &= ids

        recipes = Recipe.objects.filter(id__in=result)
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def recipe(request, id):
    if request.method == 'GET':
        try:
            recipe = Recipe.objects.get(pk=id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'No recipes with such id found'}, status=status.HTTP_404_NOT_FOUND)
        recipe_serializer = RecipeSerializer(recipe)
        ingredients = Ingredient.objects.filter(recipe=recipe)
        ingredients_serializer = IngredientSerializer(ingredients, many=True)

        result = dict(recipe_serializer.data)
        result['ingredients'] = []
        for el in ingredients_serializer.data:
            result['ingredients'].append(el['description'])

        return Response(result, status=status.HTTP_200_OK)


# переробити
@api_view(['GET'])
def get_recipes_by_time(request, time, count):
    if request.method == 'GET':
        try:
            recipes = Recipe.objects.filter(time=time)[:count]
            serializer = RecipeSerializer(recipes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.ObjectDoesNotExist:
            return Response({'message': 'Invalid time'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_hot_recipes(request, count):
    if request.method == 'GET':
        recipes = Recipe.objects.all().annotate(avg=Avg('rating__rating')).order_by('-avg')[:count]
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE', 'POST'])
def add_or_remove_favourites(request, user_id, recipe_id):
    fav_db_entry = Favourites.objects.filter(user_id=user_id, recipe_id=recipe_id)
    if request.method == 'POST':
        if fav_db_entry:
            return Response({'message': 'The recipe is already in favourites.'}, status=status.HTTP_400_BAD_REQUEST)
        fav = Favourites()
        user = User.objects.filter(pk=user_id)
        recipe = Recipe.objects.filter(pk=recipe_id)
        if user:
            if recipe:
                fav.user = user.get()
                fav.recipe = recipe.get()
                fav.save()
                return Response({'message': 'The recipe has been successfully added to favourite list.'},
                                status=status.HTTP_201_CREATED)
            return Response({'message': 'The recipe does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        if fav_db_entry:
            fav_db_entry.delete()
            return Response({'message': 'The recipe has been removed from favourites.'}, status=status.HTTP_200_OK)
        return Response({'message': 'The recipe does not exist.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_favourites_by_user_id(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(pk=user_id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        result = []
        user_favs = Favourites.objects.filter(user=user)
        for fav in user_favs:
            recipe = Recipe.objects.get(pk=fav.recipe_id)
            serialized_recipe = RecipeSerializer(recipe)
            result.append(dict(serialized_recipe.data))
        return Response(result, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
def rating(request):
    if request.method == 'POST':
        user_id = request.data['user_id']
        recipe_id = request.data['recipe_id']
        value = request.data['value']

        r = Rating()
        try:
            r.user_id = user_id
        except models.ObjectDoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            r.recipe_id = recipe_id
        except models.ObjectDoesNotExist:
            return Response({'message': 'Recipe does not exist'}, status=status.HTTP_404_NOT_FOUND)
        r.rating = value

        serializer = RatingSerializer(data=r.__dict__)
        if not serializer.is_valid():
            return Response({'message': 'Invalid rating value'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            r.save()
        except IntegrityError:
            existing_rating = Rating.objects.get(user_id=user_id, recipe_id=recipe_id)
            old_value = existing_rating.rating
            existing_rating.rating = value
            existing_rating.save()
            return Response({'message': 'Changed rating value',
                             'old_value': old_value}, status=status.HTTP_200_OK)

        return Response({'message': 'Rating successfully added'}, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        user_id = request.data['user_id']
        recipe_id = request.data['recipe_id']

        try:
            r = Rating.objects.get(user_id=user_id, recipe_id=recipe_id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'Rating does not exist'}, status=status.HTTP_404_NOT_FOUND)

        r.delete()
        return Response({'message': 'Rating successfully deleted'}, status=status.HTTP_200_OK)


# development purposes only.
@api_view(['GET'])
@permission_classes([IsAdminUser])
def temp(request):
    # fm = FilterManager()
    # recipes = Recipe.objects.all()
    # result = []
    # recipes = fm.apply_filters(['order_by_difficulty_desc'], recipes)
    # for el in recipes:
    #     result.append(dict(RecipeSerializer(el).data))
    # return Response(result, status.HTTP_200_OK)
    ratings = Rating.objects.all()
    serializer = RatingSerializer(ratings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# development purposes only.
@api_view(['POST'])
@permission_classes([IsAdminUser])
def fill_db(request):
    recipes = Recipe.objects.all()
    recipes.delete()
    ingredients = Ingredient.objects.all()
    ingredients.delete()
    ratings = Rating.objects.all()
    ratings.delete()
    favourites = Favourites.objects.all()
    favourites.delete()
    with request.FILES['file'] as f:
        data = json.loads(f.read())
        c = 0
        for el in data:
            c += 1
            if c == 200:
                break
            recipe = Recipe()
            recipe.difficulty = random.randint(1, 5)
            recipe.description = el['instructions']
            recipe.name = el['title']
            recipe.img_path = el['image']
            recipe.est_time = el['total_time']
            try:
                recipe.calories = el['nutrients']['calories']
                recipe.proteins = el['nutrients']['proteinContent']
                recipe.fats = el['nutrients']['fatContent']
                recipe.carbs = el['nutrients']['carbohydrateContent']
                recipe.yields = el['yields']
                recipe.time = random.randint(1, 3)
            except (KeyError, TypeError,):
                pass

            try:
                recipe.save()
            except Exception as e:
                print(e)
                continue

            for i in el['ingredients']:
                ingredient = Ingredient()
                ingredient.recipe = recipe
                ingredient.description = i
                try:
                    ingredient.save()
                except Exception as e:
                    print(e)
                    continue

            rating = Rating()
            rating.user = User.objects.get(pk=1)
            rating.recipe = recipe
            rating.rating = random.randint(1, 5)
            try:
                rating.save()
            except Exception as e:
                print(e)
                continue

            a = random.randint(1, 50)
            if a == 42:
                favourite = Favourites()
                favourite.user = User.objects.get(pk=1)
                favourite.recipe = recipe
                favourite.save()

    return Response()
