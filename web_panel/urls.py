from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace_view, name='marketplace_view'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
]