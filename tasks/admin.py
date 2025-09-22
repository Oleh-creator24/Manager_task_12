
import datetime
import json

from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.test import Client


try:
    from .models import Status, Task, SubTask, Category
    HAS_CATEGORY = True
except Exception:
    from .models import Status, Task, SubTask
    Category = None
    HAS_CATEGORY = False


# -------------------- Фильтры «вчера» --------------------

class YesterdayDeadlineFilter(admin.SimpleListFilter):
    title = "Дедлайн: вчера"
    parameter_name = "deadline_yesterday"
    def lookups(self, request, model_admin): return (("1", "Показать"),)
    def queryset(self, request, queryset):
        if self.value() == "1":
            yday = (timezone.now() - datetime.timedelta(days=1)).date()
            return queryset.filter(deadline__date=yday)
        return queryset

class YesterdayCreatedFilter(admin.SimpleListFilter):
    title = "Создано: вчера"
    parameter_name = "created_yesterday"
    def lookups(self, request, model_admin): return (("1", "Показать"),)
    def queryset(self, request, queryset):
        if self.value() == "1":
            yday = (timezone.now() - datetime.timedelta(days=1)).date()
            return queryset.filter(created_at__date=yday)
        return queryset


# -------------------- Инлайн подзадач

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ['title', 'description', 'status', 'deadline', 'created_at']
    readonly_fields = ('created_at',)


# -------------------- Форма Task с валидацией дедлайна (Задание 4)

class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline is None:
            return deadline
        if deadline < timezone.now():
            raise forms.ValidationError("Нельзя устанавливать дедлайн в прошлом.")
        return deadline


# -------------------- Task

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
        ('Подзадачи', {'description': "Инлайны ниже позволяют проверить связь задача ↔ подзадачи.", 'fields': tuple()}),
        ('Проверка вложенного сериализатора', {
            'description': "JSON из TaskDetailSerializer (задание 3).",
            'fields': ('api_detail_preview',),
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
        return format_html(
            '<span style="padding:2px 6px;border-radius:10px;{}">{}</span>',
            'background:#fee; color:#a00; border:1px solid #fbb;' if overdue else
            'background:#efe; color:#060; border:1px solid #beb;',
            "Просрочена" if overdue else "Ок"
        )
    is_overdue_badge.short_description = "Статус дедлайна"

    def api_detail_preview(self, obj):
        # JSON превью из TaskDetailSerializer для фиксации задания 3
        try:
            from .serializers import TaskDetailSerializer
            data = TaskDetailSerializer(obj).data
            pretty = json.dumps(data, ensure_ascii=False, indent=2)
            return format_html(
                '<details><summary style="cursor:pointer">Показать JSON</summary>'
                '<pre style="white-space:pre-wrap; margin-top:8px;">{}</pre>'
                '</details>',
                pretty
            )
        except Exception as e:
            return format_html('<code>Ошибка рендера: {}</code>', str(e))
    api_detail_preview.short_description = "TaskDetailSerializer JSON"


# -------------------- SubTask (с проверками CBV из задания 5)

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
        ('Проверка CBV (задание 5)', {
            'description': "Ссылки на эндпоинты CBV и подсказка для проверки из браузера/консоли.",
            'fields': ('cbv_api_endpoints',),
        }),
    )

    def short_title(self, obj): return obj.short_title()
    short_title.short_description = 'Title'

    # Кликабельная ссылка на GET эндпоинт CBV
    def cbv_link(self, obj):
        url = reverse('subtask-detail-update-delete', kwargs={'pk': obj.pk})
        return format_html('<a href="{}" target="_blank">GET /api/subtasks/{}/</a>', url, obj.pk)
    cbv_link.short_description = "CBV GET"

    # Блок с ссылками/подсказками
    def cbv_api_endpoints(self, obj):
        url = reverse('subtask-detail-update-delete', kwargs={'pk': obj.pk})
        sample_patch = json.dumps({"description": "Обновлено через админ-смоук"}, ensure_ascii=False)
        return format_html(
            '<div>'
            '<p><b>Эндпоинт:</b> <code>{}</code></p>'
            '<p>Открой ссылку выше — это JSON GET из CBV. Для PATCH/DELETE воспользуйся консолью или кнопками «Действия» ниже.</p>'
            '<details><summary style="cursor:pointer">Пример PATCH (PowerShell)</summary>'
            '<pre>$patch = @{{ description = "Обновлено через админ-смоук" }} | ConvertTo-Json&#10;Invoke-RestMethod -Uri "http://127.0.0.1:8000{}" -Method PATCH -ContentType "application/json; charset=utf-8" -Body $patch</pre>'
            '</details>'
            '</div>',
            url, url
        )
    cbv_api_endpoints.short_description = "CBV эндпоинты"

    # --- Action 1: OPTIONS + PATCH смоук-тест против CBV ---
    def cbv_smoke_test_patch(self, request, queryset):
        """
        Для выделенных подзадач:
        - OPTIONS к /api/subtasks/<id>/
        - PATCH описание (без CSRF, т.к. CBV отключают SessionAuth и помечены csrf_exempt)
        """
        client = Client(enforce_csrf_checks=False)
        ok = 0
        msgs = []
        for obj in queryset:
            url = reverse('subtask-detail-update-delete', kwargs={'pk': obj.pk})
            # OPTIONS
            resp_opt = client.options(url)
            # PATCH
            payload = {"description": "Обновлено через admin CBV-smoke"}
            resp_pat = client.patch(url, data=json.dumps(payload), content_type="application/json")
            msgs.append(f"#{obj.pk} OPTIONS:{resp_opt.status_code} PATCH:{resp_pat.status_code}")
            if 200 <= resp_pat.status_code < 300:
                ok += 1
        self.message_user(request, f"CBV smoke-test выполнен. Успешно PATCH: {ok}/{queryset.count()}. Детали: {', '.join(msgs)}")
    cbv_smoke_test_patch.short_description = "CBV smoke-test: OPTIONS + PATCH"

    # --- Action 2: DELETE
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
    cbv_delete_via_api.short_description = "CBV: Удалить через API (опасно)"


# -------------------- Status

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# -------------------- Category

if HAS_CATEGORY and Category is not None:
    @admin.register(Category)
    class CategoryAdmin(admin.ModelAdmin):
        list_display = ("id", "name")
        search_fields = ("name",)
