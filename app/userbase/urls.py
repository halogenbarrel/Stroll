from django.urls import path
from . import views

urlpatterns = [
    path("", views.dog_list, name="dog_list"),
    path("register/", views.register, name="register"),
]
