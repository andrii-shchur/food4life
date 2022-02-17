import json
import random

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .serializers import *
from .models import *
from .forms import *

from .object_detection.detect import predict

from django.db.models import Avg
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict


def get_user_id(request):
    token_obj = AccessToken(request.META.get('HTTP_AUTHORIZATION').split()[1])
    return token_obj['user_id']


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
            if result is not None:
                return Response(result, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def search(request):
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
def recipe(request, recipe_id):
    if request.method == 'GET':
        try:
            rec = Recipe.objects.get(pk=recipe_id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'No recipes with such id found'}, status=status.HTTP_404_NOT_FOUND)
        recipe_serializer = RecipeSerializer(rec)
        ingredients = Ingredient.objects.filter(recipe=rec)
        ingredients_serializer = IngredientSerializer(ingredients, many=True)

        result = dict(recipe_serializer.data)
        result['ingredients'] = []
        for el in ingredients_serializer.data:
            result['ingredients'].append(el['description'])
        result['avg_rating'] = Recipe.objects.filter(pk=
                                                     recipe_id).annotate(avg=Avg('rating__rating')).values()[0]['avg']

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


@api_view(['GET'])
def get_similar_recipes(request):
    user_id = get_user_id(request)
    recs = {}
    favs = Favourites.objects.get(user=user_id).order_by('-id').all()[:10]
    for fav in favs:
        rec = Recommendations.objects.filter(frome_recipe=fav.recipe.id).all()
        recs.update(r.to_recipe for r in rec)
    serializer = RecipeSerializer(recs[:30], many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE', 'POST'])
def add_or_remove_favorites(request, recipe_id):
    user_id = get_user_id(request)
    fav_db_entry = Favourites.objects.filter(user_id=user_id, recipe_id=recipe_id)
    if request.method == 'POST':
        if fav_db_entry:
            return Response({'message': 'The recipe is already in favourites.'}, status=status.HTTP_400_BAD_REQUEST)
        fav = Favourites()
        user = User.objects.filter(pk=user_id)
        rec = Recipe.objects.filter(pk=recipe_id)
        if user:
            if rec:
                fav.user = user.get()
                fav.recipe = rec.get()
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
def get_favorites(request):
    user_id = get_user_id(request)
    if request.method == 'GET':
        try:
            user = User.objects.get(pk=user_id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        result = []
        user_favs = Favourites.objects.filter(user=user)
        for fav in user_favs:
            rec = Recipe.objects.get(pk=fav.recipe_id)
            serialized_recipe = RecipeSerializer(rec)
            result.append(dict(serialized_recipe.data))
        return Response(result, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
def rating(request):
    if request.method == 'POST':
        user_id = get_user_id(request)
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

        serializer = RatingSerializer(data=model_to_dict(r))
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
        user_id = get_user_id(request)
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
    # recipes = Recipe.objects.all()
    # recipes.delete()
    # ingredients = Ingredient.objects.all()
    # ingredients.delete()
    # ratings = Rating.objects.all()
    # ratings.delete()
    # favourites = Favourites.objects.all()
    # favourites.delete()
    with request.FILES['file'] as f:
        data = json.loads(f.read())
        c = 0
        for el in data:
            c += 1
            if c == 200:
                break
            rec = Recipe()
            rec.difficulty = random.randint(1, 5)
            rec.description = el['instructions']
            rec.name = el['title']
            rec.img_path = el['image']
            rec.est_time = el['total_time']
            try:
                rec.calories = el['nutrients']['calories']
                rec.proteins = el['nutrients']['proteinContent']
                rec.fats = el['nutrients']['fatContent']
                rec.carbs = el['nutrients']['carbohydrateContent']
                rec.yields = el['yields']
            except (KeyError, TypeError,):
                pass

            try:
                rec.save()
            except Exception as e:
                print(e)
                continue

            for i in el['ingredients']:
                ingredient = Ingredient()
                ingredient.recipe = rec
                ingredient.description = i
                try:
                    ingredient.save()
                except Exception as e:
                    print(e)
                    continue

            r = Rating()
            r.user = User.objects.get(pk=1)
            r.recipe = rec
            r.rating = random.randint(1, 5)
            try:
                r.save()
            except Exception as e:
                print(e)
                continue

            a = random.randint(1, 50)
            if a == 42:
                favourite = Favourites()
                favourite.user = User.objects.get(pk=1)
                favourite.recipe = rec
                favourite.save()

    return Response()
