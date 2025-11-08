from django.urls import path
from . import views

app_name = 'job_board'

urlpatterns = [
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('', views.job_list, name='job_list'),
    path('create/', views.job_create, name='job_create'),

]