from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Family, FamilyMembership


class FamilyMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = FamilyMembership
        fields = ("id", "family", "user", "user_id", "role", "linked_person", "joined_at")
        read_only_fields = ("id", "family", "joined_at")


class FamilySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.IntegerField(read_only=True, default=0)
    current_user_role = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = (
            "id",
            "name",
            "description",
            "cover_image",
            "owner",
            "privacy",
            "members_count",
            "current_user_role",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "created_at", "updated_at")

    def get_current_user_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        membership = obj.memberships.filter(user=request.user).first()
        return membership.role if membership else None


class FamilyDashboardStatsSerializer(serializers.Serializer):
    total_members = serializers.IntegerField()
    living_members = serializers.IntegerField()
    deceased_members = serializers.IntegerField()
    total_photos = serializers.IntegerField()
    total_stories = serializers.IntegerField()
    total_relationships = serializers.IntegerField()
    recent_activity = serializers.ListField(child=serializers.DictField())
