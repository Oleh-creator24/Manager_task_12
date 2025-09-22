# tasks/serializers.py
from django.utils import timezone
from rest_framework import serializers

from .models import Task, SubTask, Status

# Category может быть, а может и не быть — подключаем безопасно
try:
    from .models import Category  # type: ignore
    HAS_CATEGORY = True
except Exception:  # модель Category отсутствует
    Category = None  # type: ignore
    HAS_CATEGORY = False


# ---------- БАЗОВЫЕ ВЛОЖЕННЫЕ СЕРИАЛИЗАТОРЫ ----------

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ("id", "name")


class TaskShallowSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "deadline")


# ---------- ЗАДАНИЕ 4: TaskCreateSerializer (валидация deadline, status не обязателен) ----------

class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Создание/обновление задачи.
    - deadline не может быть в прошлом
    - статус можно не передавать: по умолчанию берём/создаём "To Do"
    - запись статуса делаем через write-only поле status_id
    """
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(),
        source="status",
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "status_id", "deadline")

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Нельзя устанавливать дедлайн в прошлом.")
        return value

    def create(self, validated_data):
        if "status" not in validated_data:
            todo, _ = Status.objects.get_or_create(name="To Do")
            validated_data["status"] = todo
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Если статус не пришёл — оставляем прежний
        return super().update(instance, validated_data)


# ---------- ЗАДАНИЕ 1: SubTaskCreateSerializer (created_at read_only) ----------

class SubTaskCreateSerializer(serializers.ModelSerializer):
    """
    Создание/обновление подзадачи.
    - created_at только для чтения
    - статус можно передать через status_id; по умолчанию "To Do"
    - задача передаётся через task_id (обязательно при создании)
    """
    created_at = serializers.DateTimeField(read_only=True)
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(),
        source="status",
        write_only=True,
        required=False
    )
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source="task",
        write_only=True,
        required=True
    )

    class Meta:
        model = SubTask
        fields = [
            "id", "title", "description",
            "status", "status_id",
            "deadline",
            "task", "task_id",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "status", "task")

    def create(self, validated_data):
        if "status" not in validated_data:
            status_obj, _ = Status.objects.get_or_create(name="To Do")
            validated_data["status"] = status_obj
        return SubTask.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


# ---------- ЗАДАНИЕ 3: Вложенные сериализаторы для детального Task ----------

class SubTaskSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)

    class Meta:
        model = SubTask
        fields = ("id", "title", "description", "status", "deadline", "created_at")


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Детальное представление задачи с вложенными подзадачами.
    """
    status = StatusSerializer(read_only=True)
    subtasks = SubTaskSerializer(many=True, read_only=True, source="subtasks")

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "deadline", "subtasks")


# ---------- Деталка SubTask для ответов API ----------

class SubTaskDetailSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    task = TaskShallowSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ("id", "title", "description", "status", "deadline", "task", "created_at")
        read_only_fields = ("id", "created_at", "status", "task")


# ---------- ЗАДАНИЕ 2: CategoryCreateSerializer (если модель есть) ----------

if HAS_CATEGORY and Category is not None:
    class CategoryCreateSerializer(serializers.ModelSerializer):
        """
        Создание/обновление категории с проверкой уникальности имени (регистронезависимо).
        """
        class Meta:
            model = Category  # type: ignore
            fields = ("id", "name")

        def _name_exists(self, name: str, exclude_pk=None) -> bool:
            qs = Category.objects.filter(name__iexact=name.strip())
            if exclude_pk is not None:
                qs = qs.exclude(pk=exclude_pk)
            return qs.exists()

        def validate_name(self, value: str):
            if self.instance:
                if self._name_exists(value, exclude_pk=self.instance.pk):
                    raise serializers.ValidationError("Категория с таким названием уже существует.")
            else:
                if self._name_exists(value):
                    raise serializers.ValidationError("Категория с таким названием уже существует.")
            return value

        def create(self, validated_data):
            name = validated_data.get("name", "").strip()
            if self._name_exists(name):
                raise serializers.ValidationError({"name": "Категория с таким названием уже существует."})
            return super().create(validated_data)

        def update(self, instance, validated_data):
            name = validated_data.get("name", instance.name).strip()
            if self._name_exists(name, exclude_pk=instance.pk):
                raise serializers.ValidationError({"name": "Категория с таким названием уже существует."})
            return super().update(instance, validated_data)
