from django.core.management.base import BaseCommand
from tasks.orm_operations import perform_all_orm_operations


class Command(BaseCommand):
    help = 'Выполняет все ORM операции для проекта Manager_task'

    def handle(self, *args, **options):
        perform_all_orm_operations()
        self.stdout.write(
            self.style.SUCCESS('✅ Все ORM операции успешно выполнены!')
        )