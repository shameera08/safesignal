"""
SafeSignal - incidents/routing.py
"""
from django.urls import re_path
from .consumers import UserNotificationConsumer, IncidentChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/notifications/$", UserNotificationConsumer.as_asgi()),
    re_path(r"ws/incident/(?P<incident_id>\d+)/chat/$", IncidentChatConsumer.as_asgi()),
]
