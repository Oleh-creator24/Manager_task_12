#!/usr/bin/env python
"""
Скрипт для запуска Django сервера с подтверждением работы
Этот файл будет запущен и результат будет виден в терминале для Git
"""
import os
import sys
import subprocess
import time
from datetime import datetime


def run_server_with_confirmation():
    """Запускает Django сервер и показывает подтверждение работы"""

    print("=" * 60)
    print("🚀 ЗАПУСК DJANGO СЕРВЕРА - ПОДТВЕРЖДЕНИЕ РАБОТЫ")
    print("=" * 60)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Проверяем что Django установлен
    try:
        import django
        print("✅ Django установлен и готов к работе")
        print(f"   Версия Django: {django.__version__}")
    except ImportError:
        print("❌ Ошибка: Django не установлен")
        print("   Выполните: pip install django")
        return False

    # Проверяем настройки
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Manager_task_12.settings')
        django.setup()
        print("✅ Настройки Django загружены корректно")
    except Exception as e:
        print(f"❌ Ошибка настроек Django: {e}")
        return False

    # Запускаем сервер в фоновом режиме
    print()
    print("🔄 Запускаем Django сервер...")
    print("   Сервер будет доступен по: http://127.0.0.1:8000/")
    print("   Админ панель: http://127.0.0.1:8000/admin/")
    print()
    print("ℹ️  Для остановки сервера нажмите Ctrl+C")
    print("=" * 60)

    # Запускаем сервер
    try:
        # Этот вызов заблокирует выполнение直到 сервер не будет остановлен
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver'])

    except KeyboardInterrupt:
        print()
        print("⏹️  Сервер остановлен пользователем")
        print("✅ Работа скрипта завершена успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        return False


if __name__ == "__main__":
    success = run_server_with_confirmation()
    sys.exit(0 if success else 1)