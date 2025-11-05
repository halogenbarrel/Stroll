from django.urls import path
from . import views

app_name = 'view_job'

urlpatterns = [
    path('<int:job_id>/', views.job_detail, name='job_detail'),
]