# Manager_task_12/urls.py
from django.contrib import admin
from django.urls import path

# FBV из tasks/views.py
from tasks.views import (
    task_list_html,
    api_create_task,
    api_task_list,
    api_task_detail,
    api_task_stats,
    api_create_subtask,   # оставим для обратной совместимости
    # api_subtask_detail, # <- специально не подключаем (заменено на CBV ниже)
    api_task_subtasks,
)

# CBV для подзадач
from tasks.views_subtasks import (
    SubTaskListCreateView,
    SubTaskDetailUpdateDeleteView,
)

urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),

    # Домашняя HTML-страница (если нужна)
    path("", task_list_html, name="home"),

    # --- Tasks API (FBV) ---
    path("api/tasks/create/", api_create_task, name="api_task_create"),
    path("api/tasks/", api_task_list, name="api_task_list"),
    path("api/tasks/<int:task_id>/", api_task_detail, name="api_task_detail"),
    path("api/tasks/<int:task_id>/subtasks/", api_task_subtasks, name="api_task_subtasks"),
    path("api/stats/", api_task_stats, name="api_task_stats"),

    # --- SubTasks API ---
    # Современные CBV-роуты:
    path("api/subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path("api/subtasks/<int:pk>/", SubTaskDetailUpdateDeleteView.as_view(), name="subtask-detail-update-delete"),

    # Обратная совместимость: старый FBV для создания (можно убрать, если не нужен)
    path("api/subtasks/create/", api_create_subtask, name="api_subtask_create"),

    # ВАЖНО: старый FBV detail выключен, чтобы не конфликтовать с CBV:
    # path("api/subtasks/<int:subtask_id>/", api_subtask_detail, name="api_subtask_detail"),
]
