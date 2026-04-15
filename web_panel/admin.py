from django.contrib import admin
from .models import Reward

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_sonechka', 'partner_name')