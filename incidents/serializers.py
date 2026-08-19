"""
SafeSignal - incidents/serializers.py (SIMPLE VERSION)
"""
from rest_framework import serializers
from .models import Incident, Response, ChatMessage


class IncidentSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(source="reporter.username", read_only=True)
    responder_count = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            "id", "reporter", "reporter_username", "type", "severity", "description",
            "ai_summary", "media_url", "latitude", "longitude",
            "radius_meters", "status", "created_at", "resolved_at", "responder_count",
        ]
        read_only_fields = ["reporter", "severity", "ai_summary", "status", "created_at", "resolved_at"]

    def get_responder_count(self, obj):
        return obj.responses.count()

    def create(self, validated_data):
        validated_data["reporter"] = self.context["request"].user
        return super().create(validated_data)


class ResponseSerializer(serializers.ModelSerializer):
    responder_username = serializers.CharField(source="responder.username", read_only=True)

    class Meta:
        model = Response
        fields = ["id", "incident", "responder", "responder_username", "status", "distance_meters", "timestamp"]
        read_only_fields = ["incident", "responder", "distance_meters", "timestamp"]

    def create(self, validated_data):
        validated_data["responder"] = self.context["request"].user
        return super().create(validated_data)


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "incident", "sender", "sender_username", "text", "original_lang", "translated_text", "timestamp"]
        read_only_fields = ["incident", "sender", "translated_text", "timestamp"]
