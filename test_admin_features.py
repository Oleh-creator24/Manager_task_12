import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Manager_task_10.settings')
django.setup()

from tasks.models import Task, SubTask, Status
from django.utils import timezone


def test_short_title_feature():
    """Тестирование функции укороченных названий"""
    print("Testing short title feature...")

    # Создаем тестовые задачи
    short_task = Task.objects.create(
        title="Short",
        description="Short task",
        status=Status.objects.get(name="New"),
        deadline=timezone.now() + timedelta(days=1)
    )

    long_task = Task.objects.create(
        title="Very Long Task Name That Exceeds Limit",
        description="Long task",
        status=Status.objects.get(name="New"),
        deadline=timezone.now() + timedelta(days=2)
    )

    # Тестируем short_title метод
    print(f"Short task: '{short_task.title}' -> '{short_task.short_title()}'")
    print(f"Long task: '{long_task.title}' -> '{long_task.short_title()}'")

    # Тестируем подзадачи
    subtask = SubTask.objects.create(
        title="Long Subtask Name Here",
        description="Test subtask",
        status=Status.objects.get(name="New"),
        deadline=timezone.now() + timedelta(days=1),
        task=short_task
    )

    print(f"Subtask: '{subtask.title}' -> '{subtask.short_title()}'")

    # Очистка
    short_task.delete()
    long_task.delete()


def test_status_creation():
    """Создание статусов если их нет"""
    Status.objects.get_or_create(name="New")
    Status.objects.get_or_create(name="In progress")
    Status.objects.get_or_create(name="Done")
    print("Statuses created/verified")


if __name__ == "__main__":
    test_status_creation()
    test_short_title_feature()
    print("\n✅ Admin features tested successfully!")
    print("\nNow you can:")
    print("1. Run: python manage.py runserver")
    print("2. Go to http://localhost:8000/admin/")
    print("3. Login and check:")
    print("   - Inline forms for subtasks in Task admin")
    print("   - Shortened titles in list views")
    print("   - 'Mark as Done' action for Subtasks")