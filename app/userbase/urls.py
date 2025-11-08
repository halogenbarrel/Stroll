from django.urls import path, include
from . import views

app_name = 'userbase'

urlpatterns = [
    #path("", views.dog_list, name="dog_list"), #moving to dogs app
    path("register/", views.register, name="register"),
    path('settings/', views.owner_settings, name='owner_settings'),
    path('edit/', views.edit_owner_profile, name='edit_owner_profile'),

]
