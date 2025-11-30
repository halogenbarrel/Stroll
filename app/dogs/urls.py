from django.urls import path
from . import views

urlpatterns = [
    path('', views.dog_list, name='dog_list'),
    path('create/', views.create_dog, name='create_dog'),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),

    path('<int:dog_id>/edit/', views.edit_dog, name='edit_dog'),
    path('<int:dog_id>/delete/', views.delete_dog, name='delete_dog'),
]
