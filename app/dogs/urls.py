from django.urls import path
from . import views

urlpatterns = [
    path('', views.dog_list, name='dog_list'),
    path('create/', views.create_dog, name='create_dog'),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
]
