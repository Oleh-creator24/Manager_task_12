from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import datetime
from .models import Task, Status
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone




def task_list_html(request):
    """HTML страница со списком задач"""
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@csrf_exempt
@require_http_methods(["POST"])
def api_create_task(request):
    """API эндпоинт для создания задачи"""
    try:
        data = json.loads(request.body)

        # Валидация обязательных полей
        if not data.get('title'):
            return JsonResponse({'error': 'Title is required'}, status=400)

        if not data.get('deadline'):
            return JsonResponse({'error': 'Deadline is required'}, status=400)

        # Упрощенная обработка даты - просто передаем строку, Django сам преобразует
        deadline_str = data['deadline']

        # Получаем или создаем статус
        status_name = data.get('status', 'To Do')
        status, created = Status.objects.get_or_create(name=status_name)

        # Создаем задачу - Django сам преобразует строку в datetime
        task = Task.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            status=status,
            deadline=deadline_str  # передаем как строку
        )

        # Перезагружаем задачу из БД чтобы получить преобразованный datetime
        task.refresh_from_db()

        return JsonResponse({
            'message': 'Task created successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status.name,
                'deadline': task.deadline.isoformat() if task.deadline else None
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_task_list(request):
    """API для получения списка задач"""
    tasks = Task.objects.all()

    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status.name,
            'deadline': task.deadline.isoformat() if task.deadline else None
        })

    return JsonResponse({'tasks': tasks_data})


@require_http_methods(["GET"])
def api_task_detail(request, task_id):
    """API для получения деталей конкретной задачи по ID"""
    task = get_object_or_404(Task, id=task_id)

    task_data = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status.name,
        'deadline': task.deadline.isoformat() if task.deadline else None,
        'subtasks': []
    }

    # Добавляем подзадачи если они есть
    for subtask in task.subtasks.all():
        task_data['subtasks'].append({
            'id': subtask.id,
            'title': subtask.title,
            'description': subtask.description,
            'status': subtask.status.name,
            'deadline': subtask.deadline.isoformat() if subtask.deadline else None
        })

    return JsonResponse(task_data)


@require_http_methods(["GET"])
def api_task_list(request):
    """API для получения списка задач с возможностью фильтрации"""
    tasks = Task.objects.all().order_by('-deadline')

    # Фильтрация по статусу (если передан параметр status)
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status__name=status_filter)

    # Фильтрация по просроченным задачам
    overdue = request.GET.get('overdue')
    if overdue and overdue.lower() == 'true':
        tasks = tasks.filter(deadline__lt=timezone.now())

    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status.name,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'is_overdue': task.deadline < timezone.now() if task.deadline else False
        })

    return JsonResponse({
        'tasks': tasks_data,
        'count': len(tasks_data),
        'filters': {
            'status': status_filter,
            'overdue': overdue
        }
    })


@require_http_methods(["GET"])
def api_task_stats(request):
    """API для получения расширенной статистики по задачам"""
    # Базовые метрики
    total_tasks = Task.objects.count()
    total_subtasks = SubTask.objects.count()

    # Статистика по статусам задач
    tasks_by_status = Task.objects.values('status__name').annotate(count=Count('id'))
    status_stats = {item['status__name']: item['count'] for item in tasks_by_status}

    # Статистика по статусам подзадач
    subtasks_by_status = SubTask.objects.values('status__name').annotate(count=Count('id'))
    subtask_status_stats = {item['status__name']: item['count'] for item in subtasks_by_status}

    # Просроченные задачи
    overdue_tasks = Task.objects.filter(deadline__lt=timezone.now()).count()
    overdue_subtasks = SubTask.objects.filter(deadline__lt=timezone.now()).count()

    # Задачи без описания
    tasks_without_description = Task.objects.filter(description='').count()
    subtasks_without_description = SubTask.objects.filter(description='').count()

    # Ближайшие дедлайны (3 ближайшие задачи)
    upcoming_tasks = Task.objects.filter(deadline__gte=timezone.now()).order_by('deadline')[:3]
    upcoming_tasks_data = [
        {
            'id': task.id,
            'title': task.title,
            'deadline': task.deadline.isoformat(),
            'days_until': (task.deadline - timezone.now()).days
        }
        for task in upcoming_tasks
    ]

    # Заполняем нулевые значения для всех статусов
    all_statuses = ['To Do', 'In Progress', 'Done']
    for status in all_statuses:
        if status not in status_stats:
            status_stats[status] = 0
        if status not in subtask_status_stats:
            subtask_status_stats[status] = 0

    return JsonResponse({
        'stats': {
            'tasks': {
                'total': total_tasks,
                'by_status': status_stats,
                'overdue': overdue_tasks,
                'without_description': tasks_without_description,
            },
            'subtasks': {
                'total': total_subtasks,
                'by_status': subtask_status_stats,
                'overdue': overdue_subtasks,
                'without_description': subtasks_without_description,
            },
            'upcoming_deadlines': upcoming_tasks_data,
        },
        'timestamp': timezone.now().isoformat(),
        'success': True
    })