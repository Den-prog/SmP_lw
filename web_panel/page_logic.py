class BaseEcoPage:
    """Базовий клас сторінки згідно з вимогою лаби [cite: 57, 70]"""
    def __init__(self, user_balance=0):
        self.user_balance = user_balance
        self.site_name = "EcoCity Management Panel"

    def render_header(self):
        return {
            "site_name": self.site_name,
            "balance": self.user_balance,
            "menu": [
                {"label": "Маркетплейс", "url_name": "marketplace_view"},
                {"label": "Кошик", "url_name": "cart_view"}
            ]
        }

    def render_footer(self):
        return {"copyright": "© 2026 EcoCity Team 1"}

class MarketplacePage(BaseEcoPage):
    """Похідний клас для сторінки товарів [cite: 60, 67]"""
    def render_body(self, items):
        return {
            "title": "Маркетплейс винагород (Промокоди)",
            "items": items
        }

class CartPage(BaseEcoPage):
    """Похідний клас для сторінки кошика [cite: 60, 68]"""
    def render_body(self, cart_items):
        return {
            "title": "Ваші обрані винагороди",
            "items": cart_items,
            "empty_msg": "Перейти до покупок" if not cart_items else "" # Вимога [cite: 76]
        }