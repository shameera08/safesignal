"""
SafeSignal - accounts/models.py (SIMPLE VERSION - no GDAL/PostGIS needed)
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = "citizen", "Citizen"
        MEDICAL = "medical", "Medical Responder"
        POLICE = "police", "Police"
        FIRE = "fire", "Fire Responder"
        VOLUNTEER = "volunteer", "Trained Volunteer"

    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITIZEN)
    verified = models.BooleanField(default=False)
    trust_score = models.IntegerField(default=50)  # 0-100
    skills = models.JSONField(default=list, blank=True)  # e.g. ["CPR", "first_aid"]

    # live location - plain floats, no GDAL needed
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
