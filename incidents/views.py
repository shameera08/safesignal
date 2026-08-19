"""
SafeSignal - incidents/views.py (SIMPLE VERSION - Haversine-based nearby search)
"""
from rest_framework import generics, permissions
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView

from .models import Incident, Response, ChatMessage
from .serializers import IncidentSerializer, ResponseSerializer, ChatMessageSerializer
from .geo_utils import haversine_distance_meters
from .tasks import broadcast_incident, run_ai_triage


class IncidentCreateView(generics.CreateAPIView):
    """POST /api/incidents/  -> creates SOS, triggers AI triage + broadcast (async)."""
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        incident = serializer.save()
        run_ai_triage.delay(incident.id)
        broadcast_incident.delay(incident.id)


class NearbyIncidentsView(APIView):
    """GET /api/incidents/nearby/?lat=..&lng=..&radius=5000 (meters)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            lat = float(request.query_params["lat"])
            lng = float(request.query_params["lng"])
        except (KeyError, ValueError):
            return DRFResponse({"error": "lat and lng are required"}, status=400)

        radius = float(request.query_params.get("radius", 5000))

        candidates = Incident.objects.filter(status__in=["open", "responders_enroute"])
        nearby = []
        for incident in candidates:
            dist = haversine_distance_meters(lat, lng, incident.latitude, incident.longitude)
            if dist <= radius:
                nearby.append((dist, incident))

        nearby.sort(key=lambda pair: pair[0])
        serializer = IncidentSerializer([i for _, i in nearby], many=True)
        return DRFResponse(serializer.data)


class IncidentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]


class RespondToIncidentView(generics.CreateAPIView):
    """POST /api/incidents/{id}/respond/"""
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(incident_id=self.kwargs["incident_id"])


class EscalateIncidentView(APIView):
    """POST /api/incidents/{id}/escalate/ - manually widen the broadcast radius."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, incident_id):
        incident = Incident.objects.get(id=incident_id)
        incident.radius_meters = int(incident.radius_meters * 1.5)
        incident.status = Incident.Status.ESCALATED
        incident.save()
        broadcast_incident.delay(incident.id)
        return DRFResponse({"radius_meters": incident.radius_meters, "status": incident.status})


class IncidentMessagesView(generics.ListCreateAPIView):
    """GET/POST /api/incidents/{id}/messages/"""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(incident_id=self.kwargs["incident_id"])

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user, incident_id=self.kwargs["incident_id"])
