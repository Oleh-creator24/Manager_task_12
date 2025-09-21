from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title

    # def clean(self):
    #     """Валидация данных перед сохранением"""
    #     if self.deadline and self.deadline < timezone.now():
    #         raise ValidationError('Дедлайн не может быть в прошлом')
    #
    #     if not self.title.strip():
    #         raise ValidationError('Название задачи не может быть пустым')
    #
    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)

    def short_title(self):
        """Возвращает укороченное название с ... если длиннее 10 символов"""
        if len(self.title) > 10:
            return f"{self.title[:10]}..."
        return self.title

    short_title.short_description = "Title"


class SubTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    deadline = models.DateTimeField()
    task = models.ForeignKey(Task, related_name='subtasks', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Добавим поле created_at

    def __str__(self):
        return self.title

    # def clean(self):
    #     """Валидация данных перед сохранением"""
    #     if self.deadline and self.deadline < timezone.now():
    #         raise ValidationError('Дедлайн не может быть в прошлом')
    #
    #     if not self.title.strip():
    #         raise ValidationError('Название подзадачи не может быть пустым')
    #
    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)

    def short_title(self):
        """Возвращает укороченное название с ... если длиннее 10 символов"""
        if len(self.title) > 10:
            return f"{self.title[:10]}..."
        return self.title

    short_title.short_description = "Title"