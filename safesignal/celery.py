"""
SafeSignal - safesignal/celery.py
Place inside your Django project folder (e.g. safesignal/safesignal/celery.py)
Also add this to safesignal/__init__.py:

    from .celery import app as celery_app
    __all__ = ("celery_app",)
"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safesignal.settings")

app = Celery("safesignal")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
