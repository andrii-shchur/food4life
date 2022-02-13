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

from .object_detection.main import predict


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


@api_view(['GET'])
def recipe(request, id):
    if request.method == 'GET':
        recipe = Recipe.objects.get(pk=id)
        recipe_serializer = RecipeSerializer(recipe)
        ingredients = Ingredient.objects.filter(recipe=recipe)
        ingredients_serializer = IngredientSerializer(ingredients, many=True)

        result = dict(recipe_serializer.data)
        result['ingredients'] = []
        for el in ingredients_serializer.data:
            result['ingredients'].append(el['description'])

        return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_prediction(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = predict(request.FILES['file'])
            return Response(result, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def fill_db(request):
    # recipes = Recipe.objects.all()
    # recipes.delete()
    # ingredients = Ingredient.objects.all()
    # ingredients.delete()
    with request.FILES['file'] as f:
        data = json.loads(f.read())
        for el in data:
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
                ingredient.save()

    return Response()
