from rest_framework import serializers

from apps.members.serializers import PersonBriefSerializer

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    person_detail = PersonBriefSerializer(source="person", read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "family",
            "person",
            "person_detail",
            "event_type",
            "title",
            "date",
            "date_text",
            "place",
            "description",
            "metadata",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
