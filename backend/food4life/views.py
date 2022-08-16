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

from .object_detection import predict

from django.db.models import Avg
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict


def get_user_id(request):
    token_obj = AccessToken(request.META.get('HTTP_AUTHORIZATION').split()[1])
    return token_obj['user_id']


def add_favorite_to_return(request, data):
    result = list(data)
    for el in result:
        el['liked'] = True if Favourites.objects.filter(user_id=get_user_id(request), recipe_id=el['id']) else False
    return result


@api_view(['POST'])
@permission_classes([])
def rt_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.data)
        if form.is_valid():
            form.save()
            return Response({'email': form.cleaned_data['email']}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def rt_logout(request):
    if request.method == 'POST':
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def rt_predict(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = predict(request.FILES['file'])
            if result is not None:
                ids = []
                for el in result:
                    ids.append(el['obj_id']+1)
                products = Product.objects.filter(id__in=ids)
                serializer = ProductSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def rt_search(request):
    if request.method == 'GET':
        products = request.data['list']

        ids = []
        i = 0
        for product in products:
            q = Ingredient.objects.filter(description__icontains=product).values()
            ids.append([])
            for el in q:
                ids[i].append(el['recipe_id'])
            i += 1

        result = set()
        if ids:
            result = set(ids[0]).intersection(*ids[1:])

        recipes = Recipe.objects.filter(id__in=result)
        serializer = RecipeSerializer(recipes, many=True)
        result = add_favorite_to_return(request, serializer.data)
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def rt_recipe(request, recipe_id):
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

        result['liked'] = True if Favourites.objects.filter(user_id=get_user_id(request), recipe_id=rec.id) else False
        result['avg_rating'] = Recipe.objects.filter(pk=
                                                     recipe_id).annotate(avg=Avg('rating__rating')).values()[0]['avg']

        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def rt_time_recipes(request, time, count):
    if request.method == 'GET':
        if time not in [1, 2, 3]:
            return Response({'message': 'Invalid time'}, status=status.HTTP_400_BAD_REQUEST)
        time_to_str = {
            1: 'breakfast',
            2: 'brunch',
            3: 'dinner',
        }
        q = Categories.objects.filter(name__icontains=time_to_str[time])[:count].values()
        result = [x['recipe_id'] for x in q]
        recipes = Recipe.objects.filter(pk__in=result)
        serializer = RecipeSerializer(recipes, many=True)
        result = add_favorite_to_return(request, serializer.data)
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def rt_hot_recipes(request, count):
    if request.method == 'GET':
        recipes = Recipe.objects.all().annotate(avg=Avg('rating__rating')).order_by('-avg')[:count]
        serializer = RecipeSerializer(recipes, many=True)
        result = add_favorite_to_return(request, serializer.data)
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def rt_similar_recipes(request):
    user_id = get_user_id(request)
    user_recommendations = set()
    favs = Favourites.objects.filter(user=user_id).order_by('-id')[:10]
    for fav in favs:
        recommended = Recommendations.objects.filter(from_recipe=fav.recipe)
        user_recommendations.update(rec.to_recipe for rec in recommended)
    serializer = RecipeSerializer(list(user_recommendations)[:30], many=True)
    result = add_favorite_to_return(request, serializer.data)
    return Response(result, status=status.HTTP_200_OK)


@api_view(['DELETE', 'POST'])
def rt_update_favourites(request, recipe_id):
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
def rt_get_favorites(request):
    user_id = get_user_id(request)
    if request.method == 'GET':
        try:
            user = User.objects.get(pk=user_id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        result = []
        user_favs = Favourites.objects.filter(user=user).order_by('-id')
        for fav in user_favs:
            rec = Recipe.objects.get(pk=fav.recipe_id)
            serialized_recipe = RecipeSerializer(rec)
            result.append(dict(serialized_recipe.data))
        return Response(result, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
def rt_update_rating(request):
    if request.method == 'POST':
        user_id = get_user_id(request)
        recipe_id = request.data['recipe_id']
        value = request.data['value']

        rating = Rating(user_id=user_id, recipe_id=recipe_id, rating=value)
        serializer = RatingSerializer(data=model_to_dict(rating))
        if not serializer.is_valid():
            return Response({'message': 'Invalid rating value'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating.save()
        except IntegrityError:
            try:
                existing_rating = Rating.objects.get(user_id=user_id, recipe_id=recipe_id)
            except models.ObjectDoesNotExist:
                return Response({'message': 'User or Recipe does not exist'}, status=status.HTTP_404_NOT_FOUND)
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
            rating = Rating.objects.get(user_id=user_id, recipe_id=recipe_id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'Rating does not exist'}, status=status.HTTP_404_NOT_FOUND)

        rating.delete()
        return Response({'message': 'Rating successfully deleted'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        user_id = get_user_id(request)
        recipe_id = request.data['recipe_id']
        try:
            rating = Rating.objects.get(user_id=user_id, recipe_id=recipe_id)
        except models.ObjectDoesNotExist:
            return Response({'message': 'Rating does not exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_200_OK)
