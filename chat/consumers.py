import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import Thread, Message
from channels.db import database_sync_to_async

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def user_in_thread(self, user_id, thread_id):
        return Thread.objects.filter(
            id=thread_id,
            users__id=user_id
        ).exists()

    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f"chat_{self.thread_id}"

        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        has_access = await self.user_in_thread(user.id, self.thread_id)

        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        message = data.get("message", "")
        file_url = data.get("file", None)
        if file_url and not file_url.startswith("/media/chat_files/"):
            file_url = None
        user_id = self.scope["user"].id

        username = self.scope["user"].get_full_name()

        msg = await self.save_message(user_id, message, file_url)


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "file": file_url,
                "username": username,
            }
        )


    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user_id, message, file_url):
        user = User.objects.get(id=user_id)
        thread = Thread.objects.filter(
            id=self.thread_id,
            users__id=user_id
        ).first()

        if not thread:
            raise Exception("Unauthorized")
        msg = Message.objects.create(
            thread=thread,
            sender=user,
            text=message,
        )

        if file_url:
            msg.file = file_url
            msg.save()

        return msg