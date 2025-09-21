from django.contrib import admin
from .models import Status, Task, SubTask


class SubTaskInline(admin.TabularInline):  # или admin.StackedInline
    model = SubTask
    extra = 1  # Количество пустых форм для добавления подзадач
    fields = ['title', 'description', 'status', 'deadline']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['short_title', 'status', 'deadline']
    list_filter = ['status', 'deadline']
    search_fields = ['title', 'description']
    date_hierarchy = 'deadline'
    inlines = [SubTaskInline]  # Добавляем инлайн формы

    def short_title(self, obj):
        return obj.short_title()

    short_title.short_description = 'Title'


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['short_title', 'task', 'status', 'deadline']
    list_filter = ['status', 'deadline']
    search_fields = ['title', 'description']
    date_hierarchy = 'deadline'
    actions = ['mark_as_done']  # Добавляем action для задания 3

    def short_title(self, obj):
        return obj.short_title()

    short_title.short_description = 'Title'

    # Задание 3: Action для пометки как Done
    def mark_as_done(self, request, queryset):
        done_status = Status.objects.get(name="Done")
        updated_count = queryset.update(status=done_status)
        self.message_user(
            request,
            f"{updated_count} подзадач помечено как выполненные"
        )

    mark_as_done.short_description = "Пометить выбранные как Done"


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']