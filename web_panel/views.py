from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .db_manager import SQLiteDBManager, DatabaseError
from .models import Reward, VisitStatistics
from .page_logic import MarketplacePage, CartPage, BaseEcoPage
from django.contrib import messages
import copy
import datetime
from .regex_utils import is_valid_url, is_valid_date, match_cron_field, is_valid_cron_syntax, is_cron_match
import threading
import time
from django.shortcuts import render, redirect
from django.core.management import call_command
from .regex_utils import is_valid_url, is_valid_date, day_of_week, text_to_html, html_to_text, is_valid_email
from .forms import CoordinateForm
from bs4 import BeautifulSoup
from .xml_utils import parse_eco_initiatives_sax, add_guestbook_entry, read_guestbook_entries

def regex_test_view(request):
    page_layout = BaseEcoPage(user_balance=0)
    today = datetime.date.today()
    stats = VisitStatistics.objects.filter(date=today).first()
    if not stats:
        stats = VisitStatistics(hosts=0, hits=0, total=0)

    context = {
        'header': page_layout.render_header(),
        'footer': page_layout.render_footer(),
        'stats': stats,  # <--- Додали передачу статистики в шаблон
    }

    if request.method == "POST":
        if 'test_url' in request.POST:
            url_input = request.POST.get('url_input', '')
            is_valid = is_valid_url(url_input)
            context['url_result'] = "Дійсна URL-адреса" if is_valid else "Недійсний формат URL"
            context['url_input'] = url_input

        elif 'test_date' in request.POST:
            date_input = request.POST.get('date_input', '')
            is_valid = is_valid_date(date_input)
            context['date_result'] = "Дійсна дата" if is_valid else "Недійсний формат дати"
            context['date_input'] = date_input

        elif 'test_weekday' in request.POST:
            weekday_input = request.POST.get('weekday_input', '')
            context['weekday_result'] = day_of_week(weekday_input)
            context['weekday_input'] = weekday_input

        elif 'text_to_html' in request.POST:
            text_input = request.POST.get('text_input', '')
            context['html_output'] = text_to_html(text_input)
            context['text_input'] = text_input
            context['conversion_mode'] = 'text_to_html'

        elif 'html_to_text' in request.POST:
            html_input = request.POST.get('html_input', '')
            context['text_output'] = html_to_text(html_input)
            context['html_input'] = html_input
            context['conversion_mode'] = 'html_to_text'

        elif 'test_email' in request.POST:
            email_input = request.POST.get('email_input', '')
            is_valid = is_valid_email(email_input)
            context['email_result'] = "Коректна e-mail адреса" if is_valid else "❌ Некоректний формат e-mail"
            context['email_input'] = email_input

    return render(request, 'regex_test.html', context)


def lab2_view(request):

    db = SQLiteDBManager('db.sqlite3')

    setup_result = db.setup()

    today = datetime.date.today()
    stats = VisitStatistics.objects.filter(date=today).first()
    if not stats:
        stats = VisitStatistics(hosts=0, hits=0, total=0)

    if request.method == 'POST':
        action = request.POST.get('action')

        try:
            db.begin_transaction()

            if action == 'add_product':
                title = request.POST.get('title', '').strip()
                price = request.POST.get('price', '').strip()
                if title and price:
                    db.insert_data(title, float(price))

            elif action == 'add_many':
                raw = request.POST.get('bulk_data', '')
                rows = []
                for line in raw.strip().splitlines():
                    parts = line.split(',')
                    if len(parts) == 2:
                        rows.append((parts[0].strip(), float(parts[1].strip())))
                if rows:
                    db.insert_many(rows)

            elif action == 'delete_product':
                record_id = request.POST.get('record_id')
                if record_id:
                    db.delete_data(int(record_id))

            db.commit()

        except (DatabaseError, ValueError) as e:
            db.rollback()
            err_code = getattr(e, 'error_code', 'N/A')
            err_info = getattr(e, 'error_info', str(e))
            db.disconnect()
            return render(request, 'lab2_template.html', {
                'items': [],
                'stats': stats,
                'setup_result': setup_result,
                'db_error': str(e),
                'error_code': err_code,
                'error_info': err_info,
            })

        db.disconnect()
        return redirect('lab2_view')

    try:
        items_arr = db.fetch_all()
    except DatabaseError as e:
        items_arr = []
    db.disconnect()

    return render(request, 'lab2_template.html', {
        'items': items_arr,
        'stats': stats,
        'setup_result': setup_result,
    })


class Users:
    def __init__(self, name="Невідомий учасник", login="guest", password="no_password", sonechka_balance=0):
        self.name = name
        self.login = login
        self.password = password
        self.sonechka_balance = sonechka_balance

    def render_header(self):
        return f"Еко-профіль учасника: {self.name}"

    def render_body(self):
        return f"Логін: {self.login} | Пароль: {self.password}"

    def render_footer(self):
        return f"Доступно для маркетплейсу: {self.sonechka_balance} сонечок ☀️"

    def getInfo(self):
        return f"Ім'я: {self.name}, Логін: {self.login}, Баланс: {self.sonechka_balance}"

    def __copy__(self):
        new_user = Users(name="User", login="User", password="qwerty", sonechka_balance=self.sonechka_balance)
        return new_user


class AdminUser(Users):
    def __init__(self, name, login, password, sonechka_balance, admin_level):
        super().__init__(name, login, password, sonechka_balance)
        self.admin_level = admin_level

    def render_header(self):
        return f"👑ПАНЕЛЬ АДМІНІСТРАТОРА: {self.name} (Рівень: {self.admin_level})"

    def getInfo(self):
        base_info = super().getInfo()
        return f"[АДМІН] {base_info}, Рівень доступу: {self.admin_level}"


class VolunteerUser(Users):
    def __init__(self, name, login, password, sonechka_balance, events_attended):
        super().__init__(name, login, password, sonechka_balance)
        self.events_attended = events_attended

    def render_header(self):
        return f"🌿ПРОФІЛЬ ВОЛОНТЕРА: {self.name}"

    def getInfo(self):
        base_info = super().getInfo()
        return f"[ВОЛОНТЕР] {base_info}, Відвідано еко-заходів: {self.events_attended}"


class SuperUsers(Users):
    def __init__(self, name="Головний Адмін", login="admin_root", password="strong_password", sonechka_balance=10000,
                 character="admin"):
        super().__init__(name, login, password, sonechka_balance)
        self.character = character

    def render_header(self):
        return f"⚡ СУПЕР-КОРИСТУВАЧ: {self.name}"

    def getInfo(self):
        base_info = super().getInfo()
        return f"{base_info}, Роль (character): {self.character}"


def eco_users_view(request):
    user1 = VolunteerUser("Олексій", "eco_alex", "pass123456", 897, 5)
    user2 = AdminUser("Микита", "mykita_admin", "pass123", 1500, "Головний")
    user3 = Users("Іван", "ivan_new", "1111111", 100)
    user4 = Users()

    user5 = copy.copy(user1)
    super_user = SuperUsers("Вікторія", "Sup_us", "pass_superUser", 2000)
    super_user_2 = SuperUsers()

    today = datetime.date.today()
    stats = VisitStatistics.objects.filter(date=today).first()
    if not stats:
        stats = VisitStatistics(hosts=0, hits=0, total=0)

    context = {
        'users_list': [user1, user2, user3, user4, user5, super_user, super_user_2],
        'stats': stats
    }

    return render(request, 'users_page.html', context)


def marketplace_view(request):
    if 'user_balance' not in request.session:
        request.session['user_balance'] = 150
    page = MarketplacePage(user_balance=request.session['user_balance'])  # Припустимо, у юзера 150 сонечок
    rewards = Reward.objects.all()

    today = datetime.date.today()
    stats = VisitStatistics.objects.filter(date=today).first()
    if not stats:
        stats = VisitStatistics(hosts=0, hits=0, total=0)

    context = {
        "header": page.render_header(),
        "body": page.render_body(rewards),
        "footer": page.render_footer(),
        "stats": stats
    }
    return render(request, 'marketplace.html', context)


def add_to_cart(request):
    if request.method == "POST":
        reward_id = request.POST.get('reward_id')
        if reward_id:
            cart = request.session.get('cart', [])

            if reward_id not in cart:
                cart.append(reward_id)
            request.session['cart'] = cart
    return redirect('cart_view')


def remove_from_cart(request):
    if request.method == "POST":
        reward_id = request.POST.get('reward_id')
        cart = request.session.get('cart', [])

        if reward_id in cart:
            cart.remove(reward_id)
            request.session['cart'] = cart

    return redirect('cart_view')


def cart_checkout(request):
    if request.method == "POST":

        cart_ids = request.session.get('cart', [])
        current_balance = request.session.get('user_balance', 0)
        if cart_ids:
            bought_items = Reward.objects.filter(id__in=cart_ids)
            print("--- НОВЕ ЗАМОВЛЕННЯ ---")
            for item in bought_items:
                print(f"Товар: {item.title} | Ціна: {item.price}")

            total: float = sum(item.price for item in bought_items)
            print(f"ЗАГАЛЬНА СУМА: {total}")
            print("-----------------------")
            if current_balance >= total:
                request.session['user_balance'] = current_balance - total
                del request.session['cart']
                messages.success(request, "Замовлення оформлено успішно!")
            else:
                messages.error(request, "Недостатньо сонечок")
                print("Недостатньо сонечок для оформлення замовлення.")

    return redirect('cart_view')


def cart_view(request):
    cart_ids = request.session.get('cart', [])
    cart_items = Reward.objects.filter(id__in=cart_ids)
    if 'user_balance' not in request.session:
        request.session['user_balance'] = 150
    page = CartPage(user_balance=request.session['user_balance'])

    today = datetime.date.today()
    stats = VisitStatistics.objects.filter(date=today).first()
    if not stats:
        stats = VisitStatistics(hosts=0, hits=0, total=0)

    context = {
        "header": page.render_header(),
        "body": page.render_body(cart_items),
        "footer": page.render_footer(),
        "stats": stats
    }
    return render(request, 'cart.html', context)


def earn_sonechka(request):
    if request.method == "POST":
        current_balance = request.session.get('user_balance', 0)
        request.session['user_balance'] = current_balance + 50
    return redirect('marketplace_view')


def map_view(request):
    lat: float = 50.0152518
    lng: float = 36.2247767

    if request.method == 'POST':
        form = CoordinateForm(request.POST)
        if form.is_valid():
            lat = form.cleaned_data['lat']
            lng = form.cleaned_data['lng']
    else:
        form = CoordinateForm()

    context = {
        'form': form,
        'lat': lat,
        'lng': lng,
    }
    return render(request, 'map_page.html', context)


RUNNING_TASKS = {}


def background_worker(script_name, cron_expr, run_count):
    RUNNING_TASKS[script_name]['runs_left'] = run_count
    last_run_minute = None

    while RUNNING_TASKS.get(script_name, {}).get('is_running', False):
        runs_left = RUNNING_TASKS[script_name]['runs_left']

        if runs_left == 0:
            RUNNING_TASKS[script_name]['is_running'] = False
            break

        now = datetime.datetime.now()
        current_minute = now.strftime("%Y-%m-%d %H:%M")

        if current_minute != last_run_minute:
            if is_cron_match(cron_expr, now):
                try:
                    command_parts = script_name.split()
                    actual_command = command_parts[0]
                    command_args = command_parts[1:]

                    call_command(actual_command, *command_args)
                except Exception as e:
                    print(f"Помилка виконання {script_name}: {e}")

                last_run_minute = current_minute

                if runs_left > 0:
                    RUNNING_TASKS[script_name]['runs_left'] -= 1

                if RUNNING_TASKS[script_name]['runs_left'] == 0:
                    RUNNING_TASKS[script_name]['is_running'] = False
                    break

        time.sleep(1)


def simple_scheduler(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        script_name = request.POST.get('script_name')

        if action == 'start':
            cron_expr = request.POST.get('cron_expr', '* * * * *')
            run_count = int(request.POST.get('run_count', -1))

            if not is_valid_cron_syntax(cron_expr):
                messages.error(request, "Некоректний синтаксис cron! Використовуйте *, числа або */число.")
                return redirect('simple_scheduler')

            if script_name not in RUNNING_TASKS or not RUNNING_TASKS[script_name]['is_running']:
                RUNNING_TASKS[script_name] = {
                    'is_running': True,
                    'cron_expr': cron_expr,
                    'runs_left': run_count
                }

                t = threading.Thread(
                    target=background_worker,
                    args=(script_name, cron_expr, run_count),
                    daemon=True
                )
                t.start()
                messages.success(request, f"Потік для {script_name} запущено.")

        elif action == 'stop':
            if script_name in RUNNING_TASKS:
                RUNNING_TASKS[script_name]['is_running'] = False
                messages.success(request, f"Потік для {script_name} зупинено.")

        return redirect('simple_scheduler')

    tasks_context = []
    for name, data in RUNNING_TASKS.items():
        tasks_context.append({
            'name': name,
            'cron_expr': data['cron_expr'],
            'is_running': data['is_running'],
            'runs_left': data['runs_left']
        })

    return render(request, 'simple_scheduler.html', {'tasks': tasks_context})

def link_extractor_view(request):
    return render(request, 'link_extractor.html')

def link_extractor(request):
    header_data = {
        'site_name': 'Link extractor',
        'balance': request.session.get('user_balance', 150)
    }
    
    context = {
        'header': header_data,
        'html_content': '',
        'links': None,
        'links_count': 0,
        'error': None
    }

    if request.method == 'POST':
        html_content = request.POST.get('html_content', '').strip()
        context['html_content'] = html_content

        if not html_content:
            context['error'] = 'Будь ласка, вставте HTML-код для аналізу.'
            return render(request, 'link_extractor.html', context)

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            found_tags = soup.find_all('a', href=True)
            
            links_list = []
            for tag in found_tags:
                if is_valid_url(tag['href']):
                    links_list.append({
                        'text': tag.get_text().strip() or '–',
                        'href': tag['href']
                    })

            context['links'] = links_list
            context['links_count'] = len(links_list)

        except Exception as e:
            context['error'] = f'Error: {str(e)}'

    return render(request, 'link_extractor.html', context)

def lab4_xml_view(request):
    page_layout = BaseEcoPage(user_balance=request.session.get('user_balance', 150))
    today = datetime.date.today()
    stats = VisitStatistics.objects.filter(date=today).first()
    if not stats:
        stats = VisitStatistics(hosts=0, hits=0, total=0)

    #імітація джерела XML-даних (наприклад, відповідь від стороннього Web-сервісу)
    sample_xml_data = """<?xml version="1.0" encoding="utf-8"?>
<initiatives>
    <initiative id="1">
        <title>Еко-толока в парку</title>
        <location>Центральний сквер</location>
        <points>50</points>
    </initiative>
    <initiative id="2">
        <title>Збір сортувального пластику</title>
        <location>Головний корпус університету</location>
        <points>30</points>
    </initiative>
    <initiative id="3">
        <title>Висадка зеленої алеї</title>
        <location>Студентське містечко</location>
        <points>100</points>
    </initiative>
</initiatives>"""

    #завдання 1–3: парсинг за допомогою SAX
    sax_items = parse_eco_initiatives_sax(sample_xml_data)

    #завдання 4:додавання запису в гостьову книгу через DOM
    if request.method == "POST" and "add_entry" in request.POST:
        username = request.POST.get("username", "").strip()
        message = request.POST.get("message", "").strip()
        if username and message:
            add_guestbook_entry(username, message)
            return redirect('lab4_xml')

    #читання існуючих записів гостьової книги з файлу XML
    guestbook_entries = read_guestbook_entries()

    context = {
        'header': page_layout.render_header(),
        'footer': page_layout.render_footer(),
        'stats': stats,
        'sax_items': sax_items,  
        'guestbook_entries': guestbook_entries,
    }
    return render(request, 'lab4_xml.html', context)



#сторінка чату завдання 5
def chat_view(request):
    page_layout = BaseEcoPage(user_balance=request.session.get('user_balance', 150))
    context = {'header': page_layout.render_header(), 'footer': page_layout.render_footer()}
    return render(request, 'chat.html', context)
