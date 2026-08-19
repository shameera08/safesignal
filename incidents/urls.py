"""
SafeSignal - incidents/urls.py
"""
from django.urls import path
from .views import (
    IncidentCreateView, NearbyIncidentsView, IncidentDetailView,
    RespondToIncidentView, EscalateIncidentView, IncidentMessagesView,
)

urlpatterns = [
    path("", IncidentCreateView.as_view(), name="incident-create"),
    path("nearby/", NearbyIncidentsView.as_view(), name="incident-nearby"),
    path("<int:pk>/", IncidentDetailView.as_view(), name="incident-detail"),
    path("<int:incident_id>/respond/", RespondToIncidentView.as_view(), name="incident-respond"),
    path("<int:incident_id>/escalate/", EscalateIncidentView.as_view(), name="incident-escalate"),
    path("<int:incident_id>/messages/", IncidentMessagesView.as_view(), name="incident-messages"),
]
