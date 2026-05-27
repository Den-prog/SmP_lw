import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

#ЗАВДАННЯ 5
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #отримуємо ім'я кімнати з URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        #приєднуємо клієнта до групи (кімнати)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        #відключення клієнта від групи
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        #отримуємо повідомлення від JavaScript
        data = json.loads(text_data)
        
        #відправляємо повідомлення всім у групі
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['message'],
                'sender': data.get('sender', 'Анонім')
            }
        )

    async def chat_message(self, event):
        #відправляємо повідомлення назад у WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'time': datetime.now().strftime("%H:%M")
        }))

#ЗАВДАННЯ 6
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #всіх, хто заходить на сайт, підключаємо до глобальної групи
        await self.channel_layer.group_add("global_notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("global_notifications", self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({'message': event['message']}))