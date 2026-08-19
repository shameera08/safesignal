"""
SafeSignal - incidents/consumers.py
Two consumers:
  1. UserNotificationConsumer - each logged-in user joins "user_{id}" group,
     used by tasks.broadcast_incident to push new SOS alerts.
  2. IncidentChatConsumer - live chat room per incident.
"""
import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class UserNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send_json(event["payload"])


class IncidentChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.incident_id = self.scope["url_route"]["kwargs"]["incident_id"]
        self.group_name = f"incident_{self.incident_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        # content: {"text": "...", "sender": "username"}
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "text": content.get("text", ""),
                "sender": self.scope["user"].username if not self.scope["user"].is_anonymous else "unknown",
            },
        )

    async def chat_message(self, event):
        await self.send_json({"text": event["text"], "sender": event["sender"]})
