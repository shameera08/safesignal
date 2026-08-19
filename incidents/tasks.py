"""
SafeSignal - incidents/tasks.py (SIMPLE VERSION)
"""
import json
import os

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from .models import Incident
from .geo_utils import haversine_distance_meters


@shared_task
def broadcast_incident(incident_id):
    """
    Push the incident to every responder whose last-known lat/lng falls
    within the incident's radius.
    """
    incident = Incident.objects.select_related("reporter").get(id=incident_id)

    from accounts.models import User
    candidates = User.objects.filter(
        latitude__isnull=False, longitude__isnull=False
    ).exclude(id=incident.reporter_id)

    nearby_user_ids = [
        u.id for u in candidates
        if haversine_distance_meters(incident.latitude, incident.longitude, u.latitude, u.longitude) <= incident.radius_meters
    ]

    channel_layer = get_channel_layer()
    payload = {
        "type": "incident.alert",
        "incident_id": incident.id,
        "incident_type": incident.type,
        "severity": incident.severity,
        "description": incident.description,
        "lat": incident.latitude,
        "lng": incident.longitude,
    }

    for user_id in nearby_user_ids:
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {"type": "send.notification", "payload": payload},
        )

    return {"notified": len(nearby_user_ids)}


@shared_task
def run_ai_triage(incident_id):
    """
    Calls Claude to classify severity/type from the raw incident description
    and writes the result back onto the Incident.
    """
    import anthropic

    incident = Incident.objects.get(id=incident_id)
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""You are an emergency triage classifier. Given this bystander report,
respond ONLY with JSON: {{"severity": "low|medium|high|critical", "summary": "one clean sentence for responders"}}

Report type: {incident.type}
Report text: "{incident.description}"
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        incident.severity = result.get("severity", "medium")
        incident.ai_summary = result.get("summary", "")
        incident.save(update_fields=["severity", "ai_summary"])
    except Exception as e:
        # Graceful fallback: API down, no credits, bad response, etc.
        # Never let a triage failure block the incident from being usable.
        incident.severity = "medium"
        incident.ai_summary = "AI triage unavailable — please assess manually."
        incident.save(update_fields=["severity", "ai_summary"])
        print(f"[AI triage fallback] incident {incident.id}: {e}")

    return {"incident_id": incident.id, "severity": incident.severity}
