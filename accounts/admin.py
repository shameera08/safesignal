"""
SafeSignal - accounts/admin.py
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class SafeSignalUserAdmin(UserAdmin):
    list_display = ("username", "phone", "role", "verified", "trust_score", "last_seen")
    list_filter = ("role", "verified")
    search_fields = ("username", "phone")
    fieldsets = UserAdmin.fieldsets + (
        ("SafeSignal profile", {
            "fields": ("phone", "role", "verified", "trust_score", "skills", "latitude", "longitude")
        }),
    )
