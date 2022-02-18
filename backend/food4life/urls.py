from django.urls import path
from . import views

urlpatterns = [
    path('register', views.rt_register, name='register'),
    path('logout', views.rt_logout, name='logout'),
    path('search', views.rt_search, name='search recipes by ingredients'),
    path('recipe/<int:recipe_id>', views.rt_recipe, name='recipe by id'),
    path('predict', views.rt_predict, name='predict ingredients'),
    path('add_recipes', views.art_add_recipes, name='add recipes (admin)'),
    path('favourites/<int:recipe_id>', views.rt_update_favourites, name='add/remove favourite recipe'),
    path('favorites', views.rt_get_favorites, name='get user favourites'),
    path('hot_recipes/<int:count>', views.rt_hot_recipes, name='hot recipes'),
    path('time_recipes/<int:time>', views.rt_time_recipes, name='recipes by time'),
    path('similar_recipes', views.rt_similar_recipes, name='get similar liked recipes'),
    path('rating', views.rt_update_rating, name='add/remove/get recipe rating'),
    path('temp', views.rt_temp, name='temp'),
]
