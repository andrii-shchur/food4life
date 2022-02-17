from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('logout', views.log_out, name='logout'),
    path('search', views.search, name='recommend recipes'),
    path('recipe/<int:recipe_id>', views.recipe, name='product by id'),
    path('predict', views.get_prediction, name='predict'),
    path('add_recipes', views.fill_db, name='add recipes (admin)'),
    path('favorites/<int:recipe_id>', views.add_or_remove_favorites, name='add/remove favourites'),
    path('favorites', views.get_favorites, name='get user favourites'),
    path('hot_recipes/<int:count>', views.get_hot_recipes, name='hot recipes'),
    path('time_recipes/<int:time>', views.get_recipes_by_time, name='recipes by time'),
    path('similar_recipes', views.get_similar_recipes, name='get similar liked recipes'),
    path('rating', views.rating, name='add/delete rating'),
    path('temp', views.temp, name='temp'),
]
