from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.log_out, name='logout'),
    path('recipe/<int:id>', views.recipe, name='product by id'),
    path('predict/', views.get_prediction, name='predict'),
    path('add_recipes/', views.fill_db, name='add recipes (admin)'),
]
