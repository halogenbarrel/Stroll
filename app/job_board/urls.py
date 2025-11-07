from django.urls import path
from . import views

app_name = 'job_board'

urlpatterns = [
    path('<int:job_id>/', views.job_detail, name='job_detail'),
]