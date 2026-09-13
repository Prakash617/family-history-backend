from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import Media

class MediaSerializer(serializers.ModelSerializer):
    uploader = UserSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    person_detail = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = (
            "id",
            "family",
            "uploader",
            "person",
            "person_detail",
            "title",
            "description",
            "file",
            "url",
            "media_type",
            "mime_type",
            "file_size",
            "captured_date",
            "visibility",
            "created_at",
        )
        read_only_fields = ("id", "uploader", "created_at", "url", "file_size", "mime_type", "person_detail")

    def get_person_detail(self, obj):
        if obj.person:
            return {
                "id": str(obj.person.id),
                "full_name": obj.person.full_name,
            }
        return None

    def get_url(self, obj):
        if not obj.file:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["uploader"] = request.user
        f = validated_data.get("file")
        if f:
            validated_data["file_size"] = f.size
            validated_data["mime_type"] = getattr(f, "content_type", "")
        return super().create(validated_data)
