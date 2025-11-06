from django.urls import path, include
from . import views

app_name = 'userbase'

urlpatterns = [
    path("", views.dog_list, name="dog_list"),
    path("register/", views.register, name="register"),
]
