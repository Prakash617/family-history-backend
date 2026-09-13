from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "user",
            "family",
            "actor",
            "notification_type",
            "title",
            "message",
            "action_url",
            "is_read",
            "created_at",
        )
        read_only_fields = ("id", "user", "actor", "created_at")
