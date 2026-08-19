"""
SafeSignal - safesignal/asgi.py
Place inside your Django project folder (e.g. safesignal/safesignal/asgi.py)
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safesignal.settings")

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import incidents.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            incidents.routing.websocket_urlpatterns
        )
    ),
})
