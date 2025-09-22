from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import datetime
from .models import Task, Status, SubTask  # <— SubTask нужен
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .serializers import (TaskCreateSerializer, SubTaskCreateSerializer, SubTaskDetailSerializer,
                          TaskDetailSerializer,)


def task_list_html(request):
    """HTML страница со списком задач"""
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@csrf_exempt
@require_http_methods(["POST"])
def api_create_task(request):
    """API эндпоинт для создания задачи — теперь через TaskCreateSerializer с проверкой deadline."""
    try:
        data = json.loads(request.body)

        serializer = TaskCreateSerializer(data=data)
        if serializer.is_valid():
            task = serializer.save()  # если status присылаешь строкой — лучше маппить во view/сериализаторе отдельно
            return JsonResponse({
                'message': 'Task created successfully',
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status.name if getattr(task, "status", None) else None,
                    'deadline': task.deadline.isoformat() if task.deadline else None
                }
            }, status=201, json_dumps_params={'ensure_ascii': False})

        # Ошибки валидации DRF (включая "Нельзя устанавливать дедлайн в прошлом.")
        return JsonResponse({'error': serializer.errors}, status=400,
                            json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400,
                            json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500,
                            json_dumps_params={'ensure_ascii': False})

# def api_create_task(request):
#     """API эндпоинт для создания задачи"""
#     try:
#         data = json.loads(request.body)
#
#         # Валидация обязательных полей
#         if not data.get('title'):
#             return JsonResponse({'error': 'Title is required'}, status=400,
#                                 json_dumps_params={'ensure_ascii': False})
#
#         if not data.get('deadline'):
#             return JsonResponse({'error': 'Deadline is required'}, status=400,
#                                 json_dumps_params={'ensure_ascii': False})
#
#         # Упрощенная обработка даты - просто передаем строку, Django сам преобразует
#         deadline_str = data['deadline']
#
#         # Получаем или создаем статус
#         status_name = data.get('status', 'To Do')
#         status, created = Status.objects.get_or_create(name=status_name)
#
#         # Создаем задачу - Django сам преобразует строку в datetime
#         task = Task.objects.create(
#             title=data['title'],
#             description=data.get('description', ''),
#             status=status,
#             deadline=deadline_str  # передаем как строку
#         )
#
#         # Перезагружаем задачу из БД чтобы получить преобразованный datetime
#         task.refresh_from_db()
#
#         return JsonResponse({
#             'message': 'Task created successfully',
#             'task': {
#                 'id': task.id,
#                 'title': task.title,
#                 'description': task.description,
#                 'status': task.status.name,
#                 'deadline': task.deadline.isoformat() if task.deadline else None
#             }
#         }, status=201, json_dumps_params={'ensure_ascii': False})
#
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON'}, status=400,
#                             json_dumps_params={'ensure_ascii': False})
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500,
#                             json_dumps_params={'ensure_ascii': False})


@require_http_methods(["GET"])
def api_task_detail(request, task_id):
    """
    Детали задачи: используем TaskDetailSerializer (задание 3).
    """
    task = get_object_or_404(Task, id=task_id)
    serializer = TaskDetailSerializer(task)
    return JsonResponse(serializer.data, json_dumps_params={'ensure_ascii': False})

# def api_task_list(request):
#     """API для получения списка задач"""
#     tasks = Task.objects.all()
#
#     tasks_data = []
#     for task in tasks:
#         tasks_data.append({
#             'id': task.id,
#             'title': task.title,
#             'description': task.description,
#             'status': task.status.name,
#             'deadline': task.deadline.isoformat() if task.deadline else None
#         })

    return JsonResponse({'tasks': tasks_data}, json_dumps_params={'ensure_ascii': False})


@require_http_methods(["GET"])
def api_task_detail(request, task_id):
    """API для получения деталей конкретной задачи по ID"""
    task = get_object_or_404(Task, id=task_id)
    serializer = TaskDetailSerializer(task)
    return JsonResponse(serializer.data, json_dumps_params={'ensure_ascii': False})
    # task_data = {
    #     'id': task.id,
    #     'title': task.title,
    #     'description': task.description,
    #     'status': task.status.name,
    #     'deadline': task.deadline.isoformat() if task.deadline else None,
    #     'subtasks': []
    # }


    # for subtask in task.subtasks.all():
    #     task_data['subtasks'].append({
    #         'id': subtask.id,
    #         'title': subtask.title,
    #         'description': subtask.description,
    #         'status': subtask.status.name,
    #         'deadline': subtask.deadline.isoformat() if subtask.deadline else None
    #     })
    #
    # return JsonResponse(task_data, json_dumps_params={'ensure_ascii': False})


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
    }, json_dumps_params={'ensure_ascii': False})


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
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@require_http_methods(["POST"])
def api_create_subtask(request):
    """API эндпоинт для создания подзадачи"""
    try:
        data = json.loads(request.body)

        # Базовая валидация
        if not data.get('title'):
            return JsonResponse({'error': 'Title is required'}, status=400,
                                json_dumps_params={'ensure_ascii': False})

        if not data.get('deadline'):
            return JsonResponse({'error': 'Deadline is required'}, status=400,
                                json_dumps_params={'ensure_ascii': False})

        # Валидируем и сохраняем через сериализатор (task_id и status_id обрабатываются внутри)
        serializer = SubTaskCreateSerializer(data=data)
        if serializer.is_valid():
            subtask = serializer.save()
            return JsonResponse({
                'message': 'SubTask created successfully',
                'subtask': {
                    'id': subtask.id,
                    'title': subtask.title,
                    'description': subtask.description,
                    'status': subtask.status.name,
                    'deadline': subtask.deadline.isoformat() if subtask.deadline else None,
                    'task_id': subtask.task.id,
                    'created_at': subtask.created_at.isoformat() if subtask.created_at else None
                }
            }, status=201, json_dumps_params={'ensure_ascii': False})
        else:
            return JsonResponse({'error': serializer.errors}, status=400,
                                json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400,
                            json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500,
                            json_dumps_params={'ensure_ascii': False})


@require_http_methods(["GET"])
def api_subtask_detail(request, subtask_id):
    """API для получения деталей подзадачи по ID"""
    subtask = get_object_or_404(SubTask, id=subtask_id)
    serializer = SubTaskDetailSerializer(subtask)
    return JsonResponse(serializer.data, json_dumps_params={'ensure_ascii': False})


@require_http_methods(["GET"])
def api_task_subtasks(request, task_id):
    """API для получения всех подзадач конкретной задачи"""
    task = get_object_or_404(Task, id=task_id)
    subtasks = task.subtasks.all()

    serializer = SubTaskDetailSerializer(subtasks, many=True)
    return JsonResponse({'subtasks': serializer.data, 'task_id': task_id},
                        json_dumps_params={'ensure_ascii': False})
