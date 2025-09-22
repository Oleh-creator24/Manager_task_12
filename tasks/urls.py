from django.urls import path
from . import views
from .views_subtasks import SubTaskListCreateView, SubTaskDetailUpdateDeleteView

urlpatterns = [
    # HTML
    path("", views.task_list_html, name="home"),

    # --- Tasks (FBV) ---
    path("api/tasks/create/", views.api_create_task, name="api_task_create"),
    path("api/tasks/", views.api_task_list, name="api_task_list"),
    path("api/tasks/<int:task_id>/", views.api_task_detail, name="api_task_detail"),
    path("api/tasks/<int:task_id>/subtasks/", views.api_task_subtasks, name="api_task_subtasks"),
    path("api/stats/", views.api_task_stats, name="api_task_stats"),

    # --- SubTasks (CBV) ---
    path("api/subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path("api/subtasks/<int:pk>/", SubTaskDetailUpdateDeleteView.as_view(), name="subtask-detail-update-delete"),

    # Обратная совместимость для твоих тестов (FBV create)
    path("api/subtasks/create/", views.api_create_subtask, name="api_subtask_create"),

    # ⛔ Старый FBV detail НЕ подключаем, чтобы не перехватывал PATCH/PUT/DELETE:
    # path("api/subtasks/<int:subtask_id>/", views.api_subtask_detail, name="api_subtask_detail"),
]
