from django.urls import path, include
from . import views

app_name = 'userbase'

urlpatterns = [
    path("register/", views.register, name="register"),
    path('settings/', views.owner_settings, name='owner_settings'),
    path('edit/', views.edit_profile, name='edit_profile'),

]
