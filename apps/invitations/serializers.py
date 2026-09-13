from django.utils import timezone
from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    invited_by = UserSerializer(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "id",
            "family",
            "email",
            "invited_by",
            "role",
            "token",
            "status",
            "expires_at",
            "is_valid",
            "created_at",
        )
        read_only_fields = ("id", "invited_by", "token", "status", "expires_at", "created_at", "is_valid")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["invited_by"] = request.user
        return super().create(validated_data)


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        try:
            invite = Invitation.objects.get(token=value)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token.")

        if invite.status != Invitation.Status.PENDING or timezone.now() >= invite.expires_at:
            raise serializers.ValidationError("Invitation is expired or already used.")

        self.invitation = invite
        return value
