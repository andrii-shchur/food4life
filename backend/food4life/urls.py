from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.log_out, name='logout'),
    path('product/', views.product, name='product'),
    path('predict/', views.get_prediction, name='predict'),
]
