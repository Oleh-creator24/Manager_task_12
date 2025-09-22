from django.contrib import admin
from django.urls import path
from tasks import views  # твои существующие FBV
from tasks.views_subtasks import SubTaskListCreateView, SubTaskDetailUpdateDeleteView  # наши CBV

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- существующие FBV ---
    path('', views.task_list_html, name='home'),
    path('api/tasks/create/', views.api_create_task, name='api_task_create'),
    path('api/tasks/', views.api_task_list, name='api_task_list'),
    path('api/tasks/<int:task_id>/', views.api_task_detail, name='api_task_detail'),
    path('api/stats/', views.api_task_stats, name='api_task_stats'),
    path('api/subtasks/create/', views.api_create_subtask, name='api_subtask_create'),
    # ⛔ ВАЖНО: старый detail FBV убрать/закомментировать, иначе он перехватывает PATCH/PUT/DELETE
    # path('api/subtasks/<int:subtask_id>/', views.api_subtask_detail, name='api_subtask_detail'),
    path('api/tasks/<int:task_id>/subtasks/', views.api_task_subtasks, name='api_task_subtasks'),

    # --- НОВЫЕ CBV (csrf_exempt внутри классов) ---
    path('api/subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('api/subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update-delete'),
]
