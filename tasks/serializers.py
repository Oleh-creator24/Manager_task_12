from rest_framework import serializers
from django.utils import timezone
from .models import Task, SubTask, Status


try:
    from .models import Category
    HAS_CATEGORY = True
except Exception:
    Category = None
    HAS_CATEGORY = False


# --------- Базовые сериализаторы ---------

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ("id", "name")


class TaskSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "deadline")
        read_only_fields = ("id", "status")


# --------- Задание 4: TaskCreateSerializer с проверкой deadline ---------

class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Создание задач с проверкой, что deadline не в прошлом.
    """
    title = serializers.CharField(max_length=255)

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "deadline")
        read_only_fields = ("id",)

    def validate_deadline(self, value):

        if value is None:
            return value

        now = timezone.now()

        if value < now:
            raise serializers.ValidationError("Нельзя устанавливать дедлайн в прошлом.")
        return value


# --------- Подзадачи ---------

class SubTaskCreateSerializer(serializers.ModelSerializer):
    """
    Создание подзадач:
    - created_at только для чтения
    - принимаем task_id (write_only) -> маппим в task
    - принимаем status_id (write_only) -> маппим в status
    - если статус не передан — используем "To Do"
    """
    created_at = serializers.DateTimeField(read_only=True)

    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(),
        source='status',
        write_only=True,
        required=False
    )

    task = serializers.PrimaryKeyRelatedField(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source='task',
        write_only=True
    )

    class Meta:
        model = SubTask
        fields = [
            "id",
            "title",
            "description",
            "status",     # read_only
            "status_id",  # write_only
            "deadline",
            "task",       # read_only
            "task_id",    # write_only
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "status", "task"]

    def create(self, validated_data):
        if "status" not in validated_data:
            status, _ = Status.objects.get_or_create(name="To Do")
            validated_data["status"] = status
        return SubTask.objects.create(**validated_data)


class SubTaskDetailSerializer(serializers.ModelSerializer):
    """
    Детальный просмотр подзадач (с вложенным status и task)
    """
    status = StatusSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = [
            "id", "title", "description", "status",
            "deadline", "task", "created_at"
        ]
        read_only_fields = ["id", "created_at", "status", "task"]


# --------- Вложенные подзадачи + TaskDetail (задание 3)

class SubTaskNestedSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ["id", "title", "description", "status", "deadline", "created_at"]
        read_only_fields = fields


class TaskDetailSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    subtasks = SubTaskNestedSerializer(many=True, read_only=True, source="subtasks")

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "deadline", "subtasks"]
        read_only_fields = ["id", "status", "subtasks"]


# --------- Категории (задание 2)

if HAS_CATEGORY:
    class CategoryCreateSerializer(serializers.ModelSerializer):
        """
        Создание/обновление категории с проверкой уникальности имени (case-insensitive).
        """
        name = serializers.CharField(max_length=255)

        class Meta:
            model = Category
            fields = ("id", "name")
            read_only_fields = ("id",)

        @staticmethod
        def _clean_name(name: str) -> str:
            return (name or "").strip()

        def create(self, validated_data):
            name = self._clean_name(validated_data.get("name", ""))
            if Category.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError({"name": "Категория с таким названием уже существует."})
            validated_data["name"] = name
            return Category.objects.create(**validated_data)

        def update(self, instance, validated_data):
            if "name" in validated_data:
                name = self._clean_name(validated_data.get("name", ""))
                if Category.objects.filter(name__iexact=name).exclude(pk=instance.pk).exists():
                    raise serializers.ValidationError({"name": "Категория с таким названием уже существует."})
                instance.name = name
            for field, value in validated_data.items():
                if field != "name":
                    setattr(instance, field, value)
            instance.save()
            return instance
