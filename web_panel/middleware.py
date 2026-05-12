import datetime
from .models import VisitStatistics, VisitorIP


class EcoCityCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        today = datetime.date.today()
        today_str = str(today)

        if request.session.get('counted_date') != today_str:
            ip = request.META.get('REMOTE_ADDR')
            with open('visits_log.txt', 'a') as f:
                f.write(f"{datetime.datetime.now()} - {ip} - {request.path}\n")

            stats, created = VisitStatistics.objects.get_or_create(date=today)

            visitor_exists = VisitorIP.objects.filter(ip=ip, date=today).exists()

            if not visitor_exists:
                VisitorIP.objects.create(ip=ip)
                stats.hosts += 1

            stats.hits += 1
            stats.total += 1
            stats.save()

            request.session['counted_date'] = today_str

        return self.get_response(request)