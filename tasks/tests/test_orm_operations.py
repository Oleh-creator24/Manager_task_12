from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, SubTask, Status


class ORMOperationsTest(TestCase):

    def setUp(self):
        """Настройка тестовых данных"""
        self.new_status = Status.objects.create(name="New")
        self.in_progress_status = Status.objects.create(name="In progress")
        self.done_status = Status.objects.create(name="Done")

    def test_create_operations(self):
        """Тестирование создания записей"""
        # Создаем основную задачу
        task = Task.objects.create(
            title="Prepare presentation",
            description="Prepare materials and slides",
            status=self.new_status,
            deadline=timezone.now() + timedelta(days=3)
        )

        # Создаем подзадачи
        subtask1 = SubTask.objects.create(
            title="Gather information",
            description="Find necessary information",
            status=self.new_status,
            deadline=timezone.now() + timedelta(days=2),
            task=task
        )

        subtask2 = SubTask.objects.create(
            title="Create slides",
            description="Create presentation slides",
            status=self.new_status,
            deadline=timezone.now() + timedelta(days=1),
            task=task
        )

        # Проверяем создание
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(SubTask.objects.count(), 2)
        self.assertEqual(task.subtasks.count(), 2)

    def test_read_operations(self):
        """Тестирование чтения записей"""
        # Создаем тестовые данные
        task = Task.objects.create(
            title="Test Task",
            description="Test description",
            status=self.new_status,
            deadline=timezone.now() + timedelta(days=1)
        )

        # Ищем задачи со статусом "New"
        new_tasks = Task.objects.filter(status__name="New")
        self.assertEqual(new_tasks.count(), 1)
        self.assertEqual(new_tasks.first().title, "Test Task")

    def test_update_operations(self):
        """Тестирование обновления записей"""
        task = Task.objects.create(
            title="Test Task",
            description="Test description",
            status=self.new_status,
            deadline=timezone.now() + timedelta(days=1)
        )

        # Изменяем статус
        task.status = self.in_progress_status
        task.save()

        updated_task = Task.objects.get(id=task.id)
        self.assertEqual(updated_task.status.name, "In progress")

    def test_delete_operations(self):
        """Тестирование удаления записей"""
        task = Task.objects.create(
            title="Test Task",
            description="Test description",
            status=self.new_status,
            deadline=timezone.now() + timedelta(days=1)
        )

        SubTask.objects.create(
            title="Test Subtask",
            description="Test subtask description",
            status=self.new_status,
            deadline=timezone.now() + timedelta(days=1),
            task=task
        )

        # Удаляем задачу (подзадачи должны удалиться каскадно)
        task.delete()

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(SubTask.objects.count(), 0)