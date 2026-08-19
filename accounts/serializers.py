"""
SafeSignal - accounts/serializers.py (SIMPLE VERSION)
"""
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "phone", "role", "verified",
            "trust_score", "skills", "latitude", "longitude", "last_seen",
        ]
        read_only_fields = ["verified", "trust_score", "last_seen"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "phone", "password", "role"]

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            phone=validated_data["phone"],
            role=validated_data.get("role", User.Role.CITIZEN),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
