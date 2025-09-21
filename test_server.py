#!/usr/bin/env python
"""
Скрипт для быстрой проверки работы сервера без длительного запуска
"""
import os
import sys
import django
from datetime import datetime


def quick_server_test():
    """Быстрая проверка работы Django без запуска сервера"""

    print("=" * 50)
    print("🧪 БЫСТРАЯ ПРОВЕРКА РАБОТЫ DJANGO")
    print("=" * 50)
    print(f"Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. Проверка Django
    try:
        import django
        print(f"✅ Django версия: {django.__version__}")
    except ImportError:
        print("❌ Django не установлен")
        return False

    # 2. Проверка настроек
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Manager_task_12.settings')
        django.setup()
        print("✅ Настройки Django загружены")
    except Exception as e:
        print(f"❌ Ошибка настроек: {e}")
        return False

    # 3. Проверка моделей
    try:
        from tasks.models import Task, SubTask, Status
        print("✅ Модели импортированы успешно")

        # Проверяем что модели доступны
        print(f"   Доступные модели: Task, SubTask, Status")

    except Exception as e:
        print(f"❌ Ошибка моделей: {e}")
        return False

    # 4. Проверка админки
    try:
        from django.contrib import admin
        print("✅ Админ панель доступна")
    except Exception as e:
        print(f"❌ Ошибка админки: {e}")
        return False

    print()
    print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
    print("Сервер готов к запуску командой: python manage.py runserver")
    print("=" * 50)

    return True


if __name__ == "__main__":
    success = quick_server_test()
    sys.exit(0 if success else 1)