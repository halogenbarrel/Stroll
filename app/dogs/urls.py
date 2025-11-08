from django.urls import path
from . import views

urlpatterns = [
    path('', views.dog_list, name='dog_list'),
    path('<int:dog_id>/', views.dog_detail, name='dog_detail'),
    path('create/', views.create_dog, name='create_dog'),
    path('<int:dog_id>/edit/', views.edit_dog, name='edit_dog'),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
]
