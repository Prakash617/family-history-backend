from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Family, FamilyMembership


class FamilyMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = FamilyMembership
        fields = ("id", "family", "user", "user_id", "role", "status", "linked_person", "joined_at")
        read_only_fields = ("id", "family", "joined_at")


class FamilySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.IntegerField(read_only=True, default=0)
    photos_count = serializers.IntegerField(read_only=True, default=0)
    stories_count = serializers.IntegerField(read_only=True, default=0)
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
            "photos_count",
            "stories_count",
            "current_user_role",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "created_at", "updated_at")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get("request")
        if instance.cover_image:
            try:
                if request:
                    ret["cover_image"] = request.build_absolute_uri(instance.cover_image.url)
                elif not instance.cover_image.url.startswith("http"):
                    ret["cover_image"] = f"http://localhost:8000{instance.cover_image.url}"
            except Exception:
                pass
        return ret

    def get_current_user_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        if obj.owner_id == request.user.id:
            return "OWNER"
        membership = obj.memberships.filter(user=request.user).first()
        if membership:
            if membership.status == FamilyMembership.Status.APPROVED:
                return membership.role
            elif membership.status == FamilyMembership.Status.PENDING:
                return "PENDING"
        return "VIEWER" if obj.privacy == Family.Privacy.PUBLIC else None


class FamilyDashboardStatsSerializer(serializers.Serializer):
    total_members = serializers.IntegerField()
    living_members = serializers.IntegerField()
    deceased_members = serializers.IntegerField()
    total_photos = serializers.IntegerField()
    total_stories = serializers.IntegerField()
    total_relationships = serializers.IntegerField()
    recent_activity = serializers.ListField(child=serializers.DictField())
