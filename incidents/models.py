"""
SafeSignal - incidents/models.py (SIMPLE VERSION - no GDAL/PostGIS needed)
"""
from django.conf import settings
from django.db import models


class Incident(models.Model):
    class Type(models.TextChoices):
        MEDICAL = "medical", "Medical"
        FIRE = "fire", "Fire"
        ACCIDENT = "accident", "Accident"
        CRIME = "crime", "Crime/Safety Threat"
        DISASTER = "disaster", "Natural Disaster"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESPONDERS_ENROUTE = "responders_enroute", "Responders En Route"
        RESOLVED = "resolved", "Resolved"
        ESCALATED = "escalated", "Escalated to Officials"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reported_incidents"
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, blank=True)  # AI-assigned
    description = models.TextField()
    ai_summary = models.TextField(blank=True)
    media_url = models.URLField(blank=True)

    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_meters = models.IntegerField(default=1000)  # cascades outward if unanswered

    status = models.CharField(max_length=25, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.severity or 'untriaged'}] {self.type} @ {self.created_at:%H:%M}"


class Response(models.Model):
    class Status(models.TextChoices):
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        ENROUTE = "enroute", "En Route"
        ARRIVED = "arrived", "Arrived"

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="responses")
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACKNOWLEDGED)
    distance_meters = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("incident", "responder")


class ChatMessage(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    original_lang = models.CharField(max_length=10, default="en")
    translated_text = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]


class OfficialHandoff(models.Model):
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE, related_name="handoff")
    authority_type = models.CharField(max_length=30)  # e.g. "ambulance", "police", "fire"
    report_payload = models.JSONField()
    sent_at = models.DateTimeField(auto_now_add=True)
    ack_status = models.CharField(max_length=20, default="sent")
