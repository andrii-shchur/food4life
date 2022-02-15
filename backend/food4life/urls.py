from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.log_out, name='logout'),
    path('recipe/<int:id>', views.recipe, name='product by id'),
    path('predict/', views.get_prediction, name='predict'),
    path('add_recipes/', views.fill_db, name='add recipes (admin)'),
    path('favourites/<int:user_id>/<int:recipe_id>', views.add_or_remove_favourites, name='add/remove favourites'),
    path('favourites/<int:user_id>/', views.get_favourites_by_user_id, name='get user favourites'),
    path('recipes/', views.temp, name='temp'),
]
