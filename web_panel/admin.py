from django.contrib import admin
from .models import Reward

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_price', 'partner_name')

    def get_price(self, obj):
        return f"{obj.price} сонечок"
    get_price.short_description = 'Ціна'