# tasks/views_subtasks.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication

from .models import SubTask, Task, Status
from .serializers import (
    SubTaskCreateSerializer,
    SubTaskDetailSerializer,
)

# Отключаем CSRF для удобства тестов из PowerShell/скриптов
@method_decorator(csrf_exempt, name="dispatch")
class SubTaskListCreateView(APIView):
    authentication_classes = []        # без SessionAuthentication => нет CSRF
    permission_classes = [AllowAny]

    def get(self, request):
        """
        ?task_id=<int> — вернуть подзадачи конкретной задачи
        без параметра — вернуть все подзадачи
        """
        task_id = request.GET.get('task_id')
        qs = SubTask.objects.all().select_related('task', 'status')
        if task_id:
            qs = qs.filter(task_id=task_id)
        data = SubTaskDetailSerializer(qs, many=True).data
        return Response(data, status=http_status.HTTP_200_OK)

    def post(self, request):
        """
        Создать подзадачу.
        Ожидает: title, description?, deadline, task_id, status_id?
        Поле created_at — read_only (игнорируется, если передать).
        """
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            subtask = serializer.save()
            out = SubTaskDetailSerializer(subtask).data
            return Response(out, status=http_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class SubTaskDetailUpdateDeleteView(APIView):
    authentication_classes = []   # без CSRF
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return SubTask.objects.select_related('task', 'status').get(pk=pk)
        except SubTask.DoesNotExist:
            return None

    def get(self, request, pk: int):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=http_status.HTTP_404_NOT_FOUND)
        return Response(SubTaskDetailSerializer(obj).data, status=http_status.HTTP_200_OK)

    def patch(self, request, pk: int):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=http_status.HTTP_404_NOT_FOUND)
        serializer = SubTaskCreateSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            subtask = serializer.save()
            return Response(SubTaskDetailSerializer(subtask).data, status=http_status.HTTP_200_OK)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk: int):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=http_status.HTTP_404_NOT_FOUND)
        serializer = SubTaskCreateSerializer(obj, data=request.data, partial=False)
        if serializer.is_valid():
            subtask = serializer.save()
            return Response(SubTaskDetailSerializer(subtask).data, status=http_status.HTTP_200_OK)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk: int):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=http_status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=http_status.HTTP_204_NO_CONTENT)
