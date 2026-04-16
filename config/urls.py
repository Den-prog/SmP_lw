"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web_panel import views


urlpatterns = [
    path('', views.marketplace_view, name='markerplace_view'),
    path('admin/', admin.site.urls),
    path('marketplace/', views.marketplace_view, name='marketplace_view'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('earn/', views.earn_sonechka, name='earn_sonechka'),
    path('user_page/', views.eco_users_view, name='eco_users_view'),
    
]
