from django.urls import path
from .views import TaskCreateAPIView, TaskListAPIView

urlpatterns = [
    path('tasks/', TaskListAPIView.as_view(), name='api_task_list'),
    path('tasks/create/', TaskCreateAPIView.as_view(), name='api_task_create'),
]