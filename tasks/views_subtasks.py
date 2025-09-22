
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination

from .models import SubTask
from .serializers import SubTaskCreateSerializer, SubTaskDetailSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


@method_decorator(csrf_exempt, name="dispatch")
class SubTaskListCreateView(APIView):
    """
    GET: список подзадач (?task_id=...) + пагинация
    POST: создание подзадачи
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = SubTask.objects.all().order_by("-created_at")
        task_id = request.GET.get("task_id")
        if task_id:
            qs = qs.filter(task_id=task_id)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(qs, request)
        data = SubTaskDetailSerializer(page, many=True).data
        return paginator.get_paginated_response(data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(SubTaskDetailSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class SubTaskDetailUpdateDeleteView(APIView):
    """
    GET: детальная подзадача
    PUT/PATCH: обновление
    DELETE: удаление
    """
    authentication_classes = []          # убираем SessionAuthentication
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk: int) -> SubTask:
        return get_object_or_404(SubTask, pk=pk)

    def get(self, request, pk: int):
        instance = self.get_object(pk)
        return Response(SubTaskDetailSerializer(instance).data)

    def put(self, request, pk: int):
        instance = self.get_object(pk)
        serializer = SubTaskCreateSerializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(SubTaskDetailSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk: int):
        instance = self.get_object(pk)
        serializer = SubTaskCreateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(SubTaskDetailSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk: int):
        instance = self.get_object(pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
