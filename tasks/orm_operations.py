from django.utils import timezone
from datetime import timedelta
from .models import Task, SubTask, Status


def create_initial_statuses():
    """Создание начальных статусов"""
    Status.objects.get_or_create(name="New")
    Status.objects.get_or_create(name="In progress")
    Status.objects.get_or_create(name="Done")
    print("✅ Статусы созданы: New, In progress, Done")


def perform_all_orm_operations():
    """Выполнение всех ORM операций из задания"""
    print("=" * 50)
    print("ВЫПОЛНЕНИЕ ORM ОПЕРАЦИЙ ДЛЯ MANAGER_TASK")
    print("=" * 50)

    # Создаем статусы если их нет
    create_initial_statuses()

    # Получаем объекты статусов
    new_status = Status.objects.get(name="New")
    in_progress_status = Status.objects.get(name="In progress")
    done_status = Status.objects.get(name="Done")

    # 1. СОЗДАНИЕ ЗАПИСЕЙ
    print("\n1. 🆕 СОЗДАНИЕ ЗАПИСЕЙ")
    print("-" * 30)

    # Основная задача
    main_task = Task.objects.create(
        title="Prepare presentation",
        description="Prepare materials and slides for the presentation",
        status=new_status,
        deadline=timezone.now() + timedelta(days=3)
    )
    print(f"✅ Создана задача: {main_task.title}")

    # Подзадачи
    subtask1 = SubTask.objects.create(
        title="Gather information",
        description="Find necessary information for the presentation",
        status=new_status,
        deadline=timezone.now() + timedelta(days=2),
        task=main_task
    )

    subtask2 = SubTask.objects.create(
        title="Create slides",
        description="Create presentation slides",
        status=new_status,
        deadline=timezone.now() + timedelta(days=1),
        task=main_task
    )
    print(f"✅ Созданы подзадачи: {subtask1.title}, {subtask2.title}")

    # 2. ЧТЕНИЕ ЗАПИСЕЙ
    print("\n2. 📖 ЧТЕНИЕ ЗАПИСЕЙ")
    print("-" * 30)

    # Задачи со статусом "New"
    new_tasks = Task.objects.filter(status__name="New")
    print("📋 Задачи со статусом 'New':")
    for task in new_tasks:
        print(f"   - {task.title} (дедлайн: {task.deadline.date()})")

    # Создаем просроченную подзадачу со статусом "Done" для демонстрации
    expired_subtask = SubTask.objects.create(
        title="Expired done task",
        description="This task is done but expired",
        status=done_status,
        deadline=timezone.now() - timedelta(days=5),
        task=main_task
    )

    # Подзадачи с просроченным статусом "Done"
    overdue_done_subtasks = SubTask.objects.filter(
        status__name="Done",
        deadline__lt=timezone.now()
    )
    print("\n⏰ Просроченные подзадачи со статусом 'Done':")
    for subtask in overdue_done_subtasks:
        print(f"   - {subtask.title} (дедлайн: {subtask.deadline.date()})")

    # 3. ИЗМЕНЕНИЕ ЗАПИСЕЙ
    print("\n3. ✏️ ИЗМЕНЕНИЕ ЗАПИСЕЙ")
    print("-" * 30)

    # Изменяем статус основной задачи
    main_task.status = in_progress_status
    main_task.save()
    print(f"🔄 Статус задачи '{main_task.title}' изменен на '{main_task.status}'")

    # Изменяем срок выполнения для "Gather information"
    subtask1.deadline = timezone.now() - timedelta(days=2)
    subtask1.save()
    print(f"📅 Дедлайн для '{subtask1.title}' изменен на: {subtask1.deadline.date()}")

    # Изменяем описание для "Create slides"
    old_description = subtask2.description
    subtask2.description = "Create and format presentation slides"
    subtask2.save()
    print(f"📝 Описание для '{subtask2.title}' изменено:")
    print(f"   Было: {old_description}")
    print(f"   Стало: {subtask2.description}")

    # 4. УДАЛЕНИЕ ЗАПИСЕЙ
    print("\n4. 🗑️ УДАЛЕНИЕ ЗАПИСЕЙ")
    print("-" * 30)

    # Удаляем задачу и все ее подзадачи
    task_title = "Prepare presentation"
    task_to_delete = Task.objects.get(title=task_title)
    subtasks_count = task_to_delete.subtasks.count()

    task_to_delete.delete()
    print(f"✅ Задача '{task_title}' и {subtasks_count} подзадач удалены")

    # Проверяем, что удаление прошло успешно
    remaining_tasks = Task.objects.filter(title=task_title)
    remaining_subtasks = SubTask.objects.filter(task__title=task_title)

    print(f"📊 Осталось задач с названием '{task_title}': {remaining_tasks.count()}")
    print(f"📊 Осталось подзадач для этой задачи: {remaining_subtasks.count()}")

    print("\n" + "=" * 50)
    print("ВСЕ ORM ОПЕРАЦИИ УСПЕШНО ВЫПОЛНЕНЫ! 🎉")
    print("=" * 50)


# Если файл запускается напрямую
if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Manager_task_10.settings')
    django.setup()
    perform_all_orm_operations()