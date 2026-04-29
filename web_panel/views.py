from django.shortcuts import render, redirect
from django.http import HttpResponse
from .db_manager import SQLiteDBManager, CustomDatabaseError
from .models import Reward
from .page_logic import MarketplacePage, CartPage
from django.contrib import messages
from django.shortcuts import render
import copy

def lab2_view(request):
    db = SQLiteDBManager('db.sqlite3')

    try:
        db.connect()
        db.create_table()

        if request.method == 'POST':
            if 'add_product' in request.POST:
                title = request.POST.get('title')
                price = request.POST.get('price')
                if title and price:
                    db.insert_data(title, float(price))

            elif 'delete_product' in request.POST:
                record_id = request.POST.get('record_id')
                if record_id:
                    db.delete_data(int(record_id))

            db.disconnect()
            return redirect('lab2_view')

        items_arr = db.fetch_all()
        db.disconnect()
        return render(request, 'lab2_template.html', {'items': items_arr})
    except CustomDatabaseError as e:
        return HttpResponse(f"db error {e}")

class Users:
    #завдання 3, додано початкові значення якщ
    def __init__(self, name="Невідомий учасник", login="guest", password="no_password", sonechka_balance=0):
        self.name = name
        self.login = login
        self.password = password
        self.sonechka_balance = sonechka_balance

    def render_header(self):
        """Відображає заголовок сторінки користувача"""
        return f"Еко-профіль учасника: {self.name}"

    def render_body(self):
        """Відображає основну частину (конфіденційні дані)"""
        return f"Логін: {self.login} | Пароль: {self.password}"

    def render_footer(self):
        """Відображає підвал сторінки (стан рахунку)"""
        return f"Доступно для маркетплейсу: {self.sonechka_balance} сонечок ☀️"
    
    def getInfo(self):
        return f"Ім'я: {self.name}, Логін: {self.login}, Баланс: {self.sonechka_balance}"

    def __copy__(self):
        new_user = Users(name = "User", login="User", password="qwerty", sonechka_balance=self.sonechka_balance)
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

# ЗАВДАННЯ 5: 1) описати клас SuperUsers, успадкований від класу Users;
class SuperUsers(Users):
    def __init__(self, name="Головний Адмін", login="admin_root", password="strong_password", sonechka_balance=10000, character="admin"):
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
    
    #Task 4
    user5 = copy.copy(user1)
    
    #Task 5
    super_user = SuperUsers("Вікторія", "Sup_us", "pass_superUser", 2000)
    
    #Task 6
    super_user_2 = SuperUsers()
    


    context = {
        'users_list': [user1, user2, user3, user4, user5, super_user, super_user_2]
    }
    
    return render(request, 'users_page.html', context)

def marketplace_view(request):
    # Створюємо об'єкт класу сторінки (ООП)
    if 'user_balance' not in request.session:
        request.session['user_balance'] = 150
    page = MarketplacePage(user_balance=request.session['user_balance']) # Припустимо, у юзера 150 сонечок
    rewards = Reward.objects.all()

    context = {
        "header": page.render_header(),
        "body": page.render_body(rewards),
        "footer": page.render_footer()
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
        # логіка створення запису в БД
        # списання "сонечок" с баланса користувача.

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
    """Відображення кошика з сесії]"""
    cart_ids = request.session.get('cart', [])
    cart_items = Reward.objects.filter(id__in=cart_ids)
    if 'user_balance' not in request.session:
        request.session['user_balance'] = 150
    page = CartPage(user_balance=request.session['user_balance'])
    context = {
        "header": page.render_header(),
        "body": page.render_body(cart_items),
        "footer": page.render_footer()
    }
    return render(request, 'cart.html', context)

def earn_sonechka(request):
    if request.method == "POST":
        current_balance = request.session.get('user_balance', 0)
        request.session['user_balance'] = current_balance + 50
    return redirect('marketplace_view')