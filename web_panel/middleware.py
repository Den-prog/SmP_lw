import datetime
from .models import VisitStatistics, VisitorIP

class EcoCityCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Логування у файл (як у ПЗ)
        if not request.session.get('counted', False):
            ip = request.META.get('REMOTE_ADDR')
            with open('visits_log.txt', 'a') as f:
                f.write(f"{datetime.datetime.now()} - {ip} - {request.path}\n")
            
            # 2. Робота з БД (Хости/Хіти)
            today = datetime.date.today()
            stats, created = VisitStatistics.objects.get_or_create(date=today)
            
            # Перевірка унікальності IP за сьогодні
            visitor_exists = VisitorIP.objects.filter(ip=ip, date=today).exists()
            
            if not visitor_exists:
                VisitorIP.objects.create(ip=ip)
                stats.hosts += 1
            
            stats.hits += 1
            stats.total += 1
            stats.save()
            
            request.session['counted'] = True

        return self.get_response(request)