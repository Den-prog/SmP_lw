from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone


class Command(BaseCommand):
    help = 'Додає вказану кількість "сонечок" у всі активні сесії користувачів'

    def add_arguments(self, parser):
        parser.add_argument(
            'amount',
            type=int,
            nargs='?',
            default=50,
            help='Кількість сонечок для нарахування (за замовчуванням: 50)'
        )

    def handle(self, *args, **options):
        amount = options['amount']
        updated_count = 0

        try:
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())

            for session in active_sessions:
                session_data = session.get_decoded()

                current_balance = session_data.get('user_balance', 150)

                session_data['user_balance'] = current_balance + amount

                session.session_data = Session.objects.encode(session_data)
                session.save()

                updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Успіх! Додано {amount} сонечок. Оновлено активних сесій: {updated_count}.')
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Сталася помилка: {e}'))