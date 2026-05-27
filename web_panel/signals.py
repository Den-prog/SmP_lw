from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Reward

@receiver(post_save, sender=Reward)
def notify_new_reward(sender, instance, created, **kwargs):
    if created: #якщо товар щойно створено
        channel_layer = get_channel_layer()
        #відправляємо повідомлення в глобальну групу через сокети
        async_to_sync(channel_layer.group_send)(
            "global_notifications",
            {
                "type": "send_notification",
                "message": f"🔔 Термінова новина! Додано нову винагороду: '{instance.title}' за {instance.price} сонечок!"
            }
        )