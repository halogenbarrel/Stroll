from django.urls import path
from . import views

app_name = 'job_board'

urlpatterns = [
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),

]