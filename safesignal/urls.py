"""
SafeSignal - safesignal/urls.py
Place inside your Django project folder (e.g. safesignal/safesignal/urls.py)
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/incidents/", include("incidents.urls")),
]
