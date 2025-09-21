from django.urls import path
from . import views

urlpatterns = [

    path('tasks/create/', views.api_create_task, name='api_task_create'),


    path('tasks/', views.api_task_list, name='api_task_list'),

    path('tasks/<int:task_id>/', views.api_task_detail, name='api_task_detail'),


    path('stats/', views.api_task_stats, name='api_task_stats'),
]