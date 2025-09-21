from rest_framework import serializers
from .models import Task, Status


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(),
        source='status',
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'status_id', 'deadline']
        read_only_fields = ['id', 'status']

    def create(self, validated_data):
        # Если статус не указан, используем статус "To Do" по умолчанию
        if 'status' not in validated_data:
            status, created = Status.objects.get_or_create(name='To Do')
            validated_data['status'] = status

        return Task.objects.create(**validated_data)