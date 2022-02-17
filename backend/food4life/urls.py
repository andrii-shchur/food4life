from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('logout', views.log_out, name='logout'),
    path('recommend', views.recommend, name='recommend recipes'),
    path('recipe/<int:recipe_id>', views.recipe, name='product by id'),
    path('predict', views.get_prediction, name='predict'),
    path('add_recipes', views.fill_db, name='add recipes (admin)'),
    path('favorites/<int:user_id>/<int:recipe_id>', views.add_or_remove_favorites, name='add/remove favourites'),
    path('favorites/<int:user_id>', views.get_favorites_by_user_id, name='get user favourites'),
    path('hot_recipes/<int:count>', views.get_hot_recipes, name='hot recipes'),
    path('time_recipes/<int:time>/<int:count>', views.get_recipes_by_time, name='recipes by time'),
    path('rating', views.rating, name='add/delete rating'),
    path('temp', views.temp, name='temp'),
]
