"""
SafeSignal - incidents/admin.py
"""
from django.contrib import admin
from .models import Incident, Response, ChatMessage, OfficialHandoff


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "severity", "status", "reporter", "responder_count_display", "created_at")
    list_filter = ("type", "severity", "status")
    search_fields = ("description", "reporter__username")
    readonly_fields = ("created_at",)

    def responder_count_display(self, obj):
        return obj.responses.count()
    responder_count_display.short_description = "Responders"


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "incident", "responder", "status", "timestamp")
    list_filter = ("status",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "incident", "sender", "text", "timestamp")
    search_fields = ("text",)


@admin.register(OfficialHandoff)
class OfficialHandoffAdmin(admin.ModelAdmin):
    list_display = ("id", "incident", "authority_type", "ack_status", "sent_at")
