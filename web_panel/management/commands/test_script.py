from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запуск скрипта за розкладом'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Початок виконання скрипта...'))

            self.stdout.write(self.style.SUCCESS('Скрипт успішно виконано.'))
        except Exception as e:
            logger.error(f"Помилка виконання скрипта: {e}")
            self.stdout.write(self.style.ERROR('Сталася помилка.'))