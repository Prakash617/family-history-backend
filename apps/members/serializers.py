from rest_framework import serializers

from .models import Person


class PersonSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    lifespan = serializers.CharField(read_only=True)
    birth_display = serializers.CharField(read_only=True)
    death_display = serializers.CharField(read_only=True)

    class Meta:
        model = Person
        fields = (
            "id",
            "family",
            "first_name",
            "middle_name",
            "last_name",
            "preferred_name",
            "full_name",
            "gender",
            "birth_date",
            "birth_year_approx",
            "birth_display",
            "birth_place",
            "death_date",
            "death_year_approx",
            "death_display",
            "death_place",
            "is_living",
            "lifespan",
            "biography",
            "occupation",
            "profile_photo",
            "privacy",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PersonBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    lifespan = serializers.CharField(read_only=True)

    class Meta:
        model = Person
        fields = ("id", "full_name", "first_name", "last_name", "gender", "lifespan", "is_living", "profile_photo")


class RelativeSummarySerializer(serializers.Serializer):
    parents = PersonBriefSerializer(many=True)
    spouses = PersonBriefSerializer(many=True)
    children = PersonBriefSerializer(many=True)
    siblings = PersonBriefSerializer(many=True)


class PersonDetailSerializer(PersonSerializer):
    relatives = serializers.SerializerMethodField()

    class Meta(PersonSerializer.Meta):
        fields = PersonSerializer.Meta.fields + ("relatives",)

    def get_relatives(self, obj):
        from apps.relationships.models import Relationship

        # Parents: where obj is person_b (child) and type is PARENT_CHILD
        parents = [
            r.person_a
            for r in Relationship.objects.filter(
                person_b=obj, relationship_type=Relationship.Type.PARENT_CHILD
            ).select_related("person_a")
        ]

        # Children: where obj is person_a (parent) and type is PARENT_CHILD
        children = [
            r.person_b
            for r in Relationship.objects.filter(
                person_a=obj, relationship_type=Relationship.Type.PARENT_CHILD
            ).select_related("person_b")
        ]

        # Spouses:
        spouses_a = [
            r.person_b
            for r in Relationship.objects.filter(
                person_a=obj, relationship_type__in=[Relationship.Type.SPOUSE, Relationship.Type.PARTNER]
            ).select_related("person_b")
        ]
        spouses_b = [
            r.person_a
            for r in Relationship.objects.filter(
                person_b=obj, relationship_type__in=[Relationship.Type.SPOUSE, Relationship.Type.PARTNER]
            ).select_related("person_a")
        ]
        spouses = list({s.id: s for s in spouses_a + spouses_b}.values())

        # Siblings: share same parent or explicit sibling relationship
        sibling_ids = set()
        if parents:
            parent_ids = [p.id for p in parents]
            co_children = Relationship.objects.filter(
                person_a_id__in=parent_ids,
                relationship_type=Relationship.Type.PARENT_CHILD,
            ).exclude(person_b=obj).values_list("person_b_id", flat=True)
            sibling_ids.update(co_children)

        # Also explicit siblings
        exp_a = Relationship.objects.filter(
            person_a=obj, relationship_type=Relationship.Type.SIBLING
        ).values_list("person_b_id", flat=True)
        exp_b = Relationship.objects.filter(
            person_b=obj, relationship_type=Relationship.Type.SIBLING
        ).values_list("person_a_id", flat=True)
        sibling_ids.update(exp_a)
        sibling_ids.update(exp_b)

        siblings = Person.objects.filter(id__in=sibling_ids)

        return {
            "parents": PersonBriefSerializer(parents, many=True).data,
            "spouses": PersonBriefSerializer(spouses, many=True).data,
            "children": PersonBriefSerializer(children, many=True).data,
            "siblings": PersonBriefSerializer(siblings, many=True).data,
        }
