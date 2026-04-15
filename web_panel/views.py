from django.shortcuts import render, redirect
from .models import Reward
from .page_logic import MarketplacePage, CartPage

def marketplace_view(request):
    # Створюємо об'єкт класу сторінки (ООП)
    page = MarketplacePage(user_balance=150) # Припустимо, у юзера 150 сонечок
    rewards = Reward.objects.all()
    
    context = {
        "header": page.render_header(),
        "body": page.render_body(rewards),
        "footer": page.render_footer()
    }
    return render(request, 'marketplace.html', context)

def add_to_cart(request):
    """Обробка додавання товару в сесію через POST [cite: 74]"""
    if request.method == "POST":
        reward_id = request.POST.get('reward_id')
        cart = request.session.get('cart', [])
        cart.append(reward_id)
        request.session['cart'] = cart # Збереження в сесію
    return redirect('cart_view')

def cart_view(request):
    """Відображення кошика з сесії [cite: 75]"""
    cart_ids = request.session.get('cart', [])
    cart_items = Reward.objects.filter(id__in=cart_ids)
    
    page = CartPage(user_balance=150)
    context = {
        "header": page.render_header(),
        "body": page.render_body(cart_items),
        "footer": page.render_footer()
    }
    return render(request, 'cart.html', context)