from django.contrib import admin
from django.urls import path, include
from tasks.views import api_task_list  # импортируем существующую функцию

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_task_list, name='home'),  # используем существующую функцию
    path('api/', include('tasks.urls')),   # API endpoints
]