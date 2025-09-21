# tasks/management/commands/create_initial_data.py
from django.core.management.base import BaseCommand
from tasks.models import Status

class Command(BaseCommand):
    help = 'Create initial status data'

    def handle(self, *args, **options):
        statuses = ['To Do', 'In Progress', 'Done']
        for status_name in statuses:
            Status.objects.get_or_create(name=status_name)
            self.stdout.write(
                self.style.SUCCESS(f'Created status: {status_name}')
            )