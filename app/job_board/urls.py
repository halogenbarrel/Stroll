from django.urls import path
from . import views

app_name = 'job_board'

urlpatterns = [
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('', views.job_list, name='job_list'),
    path('create/', views.job_create, name='job_create'),
    path('delete/<int:job_id>/', views.job_delete, name='job_delete'),
    path("jobs/accept/<int:job_id>/", views.accept_job, name="accept_job"),
    path("jobs/decline/<int:job_id>/", views.decline_job, name="decline_job"),
    path('jobs/confirm_walker/<int:job_id>/', views.confirm_walker, name='confirm_walker'),
    path('jobs/decline/<int:job_id>/', views.decline_job, name='decline_job'),
]
