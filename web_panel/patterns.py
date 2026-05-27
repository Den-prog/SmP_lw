import logging
from abc import ABC, abstractmethod
from .models import Reward

# ЗАВДАННЯ 2: SINGLETON (Одинак) - Роутер
class SingletonRouter:
    """
    Паттерн Singleton гарантує, що у нас є лише один екземпляр роутера
    на весь додаток.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Створюємо екземпляр лише якщо його ще не існує
            cls._instance = super(SingletonRouter, cls).__new__(cls)
            cls._instance.routes = {}
        return cls._instance

    def add_route(self, path, controller_name):
        self.routes[path] = controller_name

    def get_controller(self, path):
        return self.routes.get(path, "404_not_found")



# ЗАВДАННЯ 3: FACTORY METHOD (Фабричний метод)

class RewardFactory:
    """
    Паттерн Фабрика: інкапсулює логіку створення різних типів винагород,
    щоб не викликати конструктор моделі Reward напряму скрізь у коді.
    """
    @staticmethod
    def create_reward(reward_type, title, desc, price, partner):
        if reward_type == 'digital':
            # Цифрові товари (наприклад, промокоди) можуть мати спеціальний префікс
            return Reward(title=f"🎟 [Цифровий] {title}", desc=desc, price=price, partner_name=partner)
        elif reward_type == 'physical':
            # Фізичні товари
            return Reward(title=f"📦 [Фізичний] {title}", desc=desc, price=price, partner_name=partner)
        else:
            return Reward(title=title, desc=desc, price=price, partner_name=partner)



# ЗАВДАННЯ 4: STRATEGY (Стратегія)

class DiscountStrategy(ABC):
    """Базовий інтерфейс для стратегій розрахунку ціни."""
    @abstractmethod
    def calculate_price(self, base_price):
        pass

class SimplePriceCalculationStrategy(DiscountStrategy):
    """Стратегія: Базова ціна без знижок."""
    def calculate_price(self, base_price):
        return base_price

class VolunteerDiscountStrategy(DiscountStrategy):
    """Стратегія: Знижка 20% для активних волонтерів EcoCity."""
    def calculate_price(self, base_price):
        return base_price * 0.8


class CartCalculator:
    """Контекст, який використовує стратегію."""
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def checkout(self, base_price):
        return self.strategy.calculate_price(base_price)



# ЗАВДАННЯ 5: ADAPTER (Адаптер)

class DatabaseAdapter(ABC):
    """Загальний інтерфейс для роботи з БД."""
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def save_data(self, data):
        pass

class DjangoSQLiteAdapter(DatabaseAdapter):
    """Адаптер для стандартної SQLite (використовує Django ORM)."""
    def connect(self):
        return "Підключено до SQLite через Django ORM."
        
    def save_data(self, data):
        return f"Збережено {data} у SQLite."

class MongoDatabaseAdapter(DatabaseAdapter):
    """Адаптер для MongoDB (Імітація для виконання вимоги)."""
    def connect(self):
        return "Підключено до MongoDB Cluster."
        
    def save_data(self, data):
        return f"Документ {data} успішно вставлено в колекцію Mongo."



# ЗАВДАННЯ 6: DECORATOR (Декоратор)

def log_model_save(func):
    """
    Паттерн Декоратор (в Python реалізується нативно через @).
    Виконує логування моделі перед її збереженням у БД.
    """
    def wrapper(self, *args, **kwargs):
        # Логіка ПЕРЕД збереженням
        log_message = f"[LOG] Підготовка до запису моделі {self.__class__.__name__}: {self.title} (Ціна: {self.price})"
        print(log_message)
        
        with open('model_save_logs.txt', 'a', encoding='utf-8') as f:
            f.write(f"{log_message}\n")
            
        # Виклик оригінальної функції збереження
        return func(self, *args, **kwargs)
        
    return wrapper

Reward.save = log_model_save(Reward.save)