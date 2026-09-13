from rest_framework import serializers

from apps.members.serializers import PersonBriefSerializer

from .models import MarriagePartnership, Relationship
from .services.validation import validate_no_ancestor_cycle


class RelationshipSerializer(serializers.ModelSerializer):
    person_a_detail = PersonBriefSerializer(source="person_a", read_only=True)
    person_b_detail = PersonBriefSerializer(source="person_b", read_only=True)

    class Meta:
        model = Relationship
        fields = (
            "id",
            "family",
            "person_a",
            "person_a_detail",
            "person_b",
            "person_b_detail",
            "relationship_type",
            "relationship_subtype",
            "is_active",
            "start_date",
            "end_date",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        person_a = attrs.get("person_a")
        person_b = attrs.get("person_b")
        rel_type = attrs.get("relationship_type")

        if person_a == person_b:
            raise serializers.ValidationError("A person cannot have a relationship with themselves.")

        if person_a.family_id != person_b.family_id:
            raise serializers.ValidationError("Both people must belong to the same family.")

        if rel_type == Relationship.Type.PARENT_CHILD:
            validate_no_ancestor_cycle(person_a.id, person_b.id)

        return attrs


class MarriagePartnershipSerializer(serializers.ModelSerializer):
    partner_1_detail = PersonBriefSerializer(source="partner_1", read_only=True)
    partner_2_detail = PersonBriefSerializer(source="partner_2", read_only=True)

    class Meta:
        model = MarriagePartnership
        fields = (
            "id",
            "family",
            "partner_1",
            "partner_1_detail",
            "partner_2",
            "partner_2_detail",
            "partnership_type",
            "start_date",
            "start_place",
            "end_date",
            "end_reason",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        partner_1 = attrs.get("partner_1")
        partner_2 = attrs.get("partner_2")

        if partner_1 == partner_2:
            raise serializers.ValidationError("Partners cannot be the same person.")

        if partner_1.family_id != partner_2.family_id:
            raise serializers.ValidationError("Both partners must belong to the same family.")

        return attrs
