from rest_framework import serializers

from apps.members.serializers import PersonBriefSerializer
from apps.users.serializers import UserSerializer

from .models import Story


class StorySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    associated_people_details = PersonBriefSerializer(source="associated_people", many=True, read_only=True)

    class Meta:
        model = Story
        fields = (
            "id",
            "family",
            "author",
            "title",
            "content",
            "cover_image",
            "status",
            "associated_people",
            "associated_people_details",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at")

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

    def create(self, validated_data):
        people = validated_data.pop("associated_people", [])
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        story = Story.objects.create(**validated_data)
        if people:
            story.associated_people.set(people)
        return story
