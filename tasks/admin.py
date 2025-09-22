# tasks/admin.py
import datetime
import json

from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.test import Client

# безопасный импорт Category
try:
    from .models import Status, Task, SubTask, Category
    HAS_CATEGORY = True
except Exception:
    from .models import Status, Task, SubTask
    Category = None
    HAS_CATEGORY = False


# --- Фильтры "вчера" ---

class YesterdayDeadlineFilter(admin.SimpleListFilter):
    title = "Дедлайн: вчера"
    parameter_name = "deadline_yesterday"
    def lookups(self, request, model_admin): return (("1", "Показать"),)
    def queryset(self, request, qs):
        if self.value() == "1":
            d = (timezone.now() - datetime.timedelta(days=1)).date()
            return qs.filter(deadline__date=d)
        return qs

class YesterdayCreatedFilter(admin.SimpleListFilter):
    title = "Создано: вчера"
    parameter_name = "created_yesterday"
    def lookups(self, request, model_admin): return (("1", "Показать"),)
    def queryset(self, request, qs):
        if self.value() == "1":
            d = (timezone.now() - datetime.timedelta(days=1)).date()
            return qs.filter(created_at__date=d)
        return qs


# --- Инлайн подзадач ---

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ['title', 'description', 'status', 'deadline', 'created_at']
    readonly_fields = ('created_at',)


# --- Форма Task с валидацией дедлайна (Задание 4) ---

class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Нельзя устанавливать дедлайн в прошлом.")
        return deadline


# --- TaskAdmin ---

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ['short_title', 'status', 'deadline', 'is_overdue_badge', 'subtasks_count']
    list_filter = ['status', 'deadline', YesterdayDeadlineFilter]
    search_fields = ['title', 'description']
    date_hierarchy = 'deadline'
    inlines = [SubTaskInline]
    readonly_fields = ('api_detail_preview',)

    fieldsets = (
        (None, {'fields': ('title', 'description', 'status', 'deadline')}),
        ('Подзадачи', {'fields': tuple(), 'description': "Инлайны ниже позволяют проверить связь задача ↔ подзадачи."}),
        ('Проверка вложенного сериализатора', {
            'fields': ('api_detail_preview',),
            'description': "JSON из TaskDetailSerializer (задание 3).",
        }),
    )

    def short_title(self, obj): return obj.short_title()
    short_title.short_description = 'Title'

    def subtasks_count(self, obj): return obj.subtasks.count()
    subtasks_count.short_description = "Подзадач"

    def is_overdue_badge(self, obj):
        if not obj.deadline:
            return "-"
        overdue = obj.deadline < timezone.now()
        style = ('background:#fee; color:#a00; border:1px solid #fbb;'
                 if overdue else
                 'background:#efe; color:#060; border:1px solid #beb;')
        text = "Просрочена" if overdue else "Ок"
        return format_html('<span style="padding:2px 6px;border-radius:10px;{}">{}</span>', style, text)
    is_overdue_badge.short_description = "Статус дедлайна"

    def api_detail_preview(self, obj):
        try:
            from .serializers import TaskDetailSerializer
            pretty = json.dumps(TaskDetailSerializer(obj).data, ensure_ascii=False, indent=2)
            return format_html(
                '<details><summary style="cursor:pointer">Показать JSON</summary>'
                '<pre style="white-space:pre-wrap; margin-top:8px;">{}</pre>'
                '</details>',
                pretty
            )
        except Exception as e:
            return format_html('<code>Ошибка рендера: {}</code>', str(e))
    api_detail_preview.short_description = "TaskDetailSerializer JSON"


# --- SubTaskAdmin: ссылки на CBV + smoke-тесты ---

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['short_title', 'task', 'status', 'deadline', 'created_at', 'cbv_link']
    list_filter = ['status', 'deadline', 'created_at', YesterdayDeadlineFilter, YesterdayCreatedFilter]
    search_fields = ['title', 'description', 'task__title']
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'cbv_api_endpoints')
    actions = ['cbv_smoke_test_patch', 'cbv_delete_via_api']

    fieldsets = (
        (None, {'fields': ('title', 'description', 'status', 'task', 'deadline')}),
        ('Технические поля', {'fields': ('created_at',)}),
        ('Проверка CBV (задание 5)', {'fields': ('cbv_api_endpoints',)}),
    )

    def short_title(self, obj): return obj.short_title()
    short_title.short_description = 'Title'

    def cbv_link(self, obj):
        url = reverse('subtask-detail-update-delete', kwargs={'pk': obj.pk})
        return format_html('<a href="{}" target="_blank">GET /api/subtasks/{}/</a>', url, obj.pk)
    cbv_link.short_description = "CBV GET"

    def cbv_api_endpoints(self, obj):
        url = reverse('subtask-detail-update-delete', kwargs={'pk': obj.pk})
        return format_html(
            '<div><p><b>Эндпоинт:</b> <code>{}</code></p>'
            '<p>Открой ссылку — JSON из CBV. Для PATCH/DELETE используй actions ниже.</p></div>',
            url
        )
    cbv_api_endpoints.short_description = "CBV эндпоинты"

    def cbv_smoke_test_patch(self, request, queryset):
        client = Client(enforce_csrf_checks=False)
        ok = 0
        msgs = []
        for obj in queryset:
            url = reverse('subtask-detail-update-delete', kwargs={'pk': obj.pk})
            resp_opt = client.options(url)
            payload = {"description": "Обновлено через admin CBV-smoke"}
            resp_pat = client.patch(url, data=json.dumps(payload), content_type="application/json")
            msgs.append(f"#{obj.pk} OPTIONS:{resp_opt.status_code} PATCH:{resp_pat.status_code}")
            if 200 <= resp_pat.status_code < 300:
                ok += 1
        self.message_user(request, f"CBV smoke-test: PATCH ok {ok}/{queryset.count()}. Детали: {', '.join(msgs)}")
    cbv_smoke_test_patch.short_description = "CBV smoke-test: OPTIONS + PATCH"

    def cbv_delete_via_api(self, request, queryset):
        client = Client(enforce_csrf_checks=False)
        deleted = 0
        msgs = []
        for obj in queryset:
            url = reverse('subtask-detail-update-delete', kwargs={'pk': obj.pk})
            resp = client.delete(url)
            msgs.append(f"#{obj.pk} DEL:{resp.status_code}")
            if resp.status_code == 204:
                deleted += 1
        self.message_user(request, f"Удалено через CBV: {deleted}/{queryset.count()}. Статусы: {', '.join(msgs)}")
    cbv_delete_via_api.short_description = "CBV: Удалить через API (осторожно)"


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


if HAS_CATEGORY and Category is not None:
    @admin.register(Category)
    class CategoryAdmin(admin.ModelAdmin):
        list_display = ("id", "name")
        search_fields = ("name",)

