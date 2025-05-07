# chats/consumers.py
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.db import models
from accounts.models import User
from chats.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(
            f"WebSocket auth check - user type: {type(self.scope['user'])}, user: {self.scope['user']}, is_authenticated: {getattr(self.scope['user'], 'is_authenticated', False)}")
        self.user = self.scope['user']
        if self.user.is_anonymous:
            print("WebSocket rejected - anonymous user")
            await self.close()
            return

        self.user_id = str(self.user.pk)

        # Modify the room_group_name to ensure consistency
        # The format must be the same for both users to receive messages
        self.room_group_name = f'chat_user_{self.user_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )



        await self.accept()
        print(f"WebSocket connected for user {self.user_id}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected for user {self.user_id}, code: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type", "chat_message")

        if message_type == "read_receipt":
           await self.read_message(text_data)
        else:
            message = data.get('content')
            sender_id = self.user_id
            to_user_id = data.get('to_user_id')

            # Save the message to the database
            message_db = await self.save_message(sender_id, to_user_id, message)

            # Format the message for sending
            message_data = {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'to_user_id': to_user_id,
                'message_id': message_db.pk,
                'created_at': str(message_db.created_at)
            }

            # Send message to sender's room group
            await self.channel_layer.group_send(
                self.room_group_name,
                message_data
            )

            # Send message to receiver's room group
            receiver_room_group_name = f'chat_user_{to_user_id}'
            await self.channel_layer.group_send(
                receiver_room_group_name,
                message_data
            )

            print(f"Message sent from {sender_id} to {to_user_id}: {message[:20]}...")

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'to_user_id': event['to_user_id'],
            'message_id': event['message_id'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content
        )
        return message

    async def read_message(self, text_data):
        data = json.loads(text_data)
        message_id = data.get("message_id")

        await self.mark_message_as_read(message_id)

        message = await self.message_details(message_id)

        sender_id = str(message.sender.pk)
        sender_room_group_name = f"chat_user_{sender_id}"

        await self.channel_layer.group_send(
            sender_room_group_name,
            {
                "type": "read_status",
                "message_id": message_id,
                "reader_id": self.user.pk
            }
        )

    async def read_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "read_status",
            "message_id": event['message_id'],
            "reader_id": event['reader_id']
        }))

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id, receiver=self.user)
            message.is_read = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def message_details(self, message_id):
        return Message.objects.select_related('sender').filter(id=message_id).first()