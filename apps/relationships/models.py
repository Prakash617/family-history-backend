import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.families.models import Family
from apps.members.models import Person


class Relationship(models.Model):
    """
    Directional genealogical or legal edge between two people.
    For PARENT_CHILD: person_a is Parent, person_b is Child.
    """
    class Type(models.TextChoices):
        PARENT_CHILD = "PARENT_CHILD", "Parent - Child"
        SPOUSE = "SPOUSE", "Spouse"
        PARTNER = "PARTNER", "Partner"
        SIBLING = "SIBLING", "Sibling"
        GUARDIAN = "GUARDIAN", "Guardian - Ward"

    class Subtype(models.TextChoices):
        BIOLOGICAL = "BIOLOGICAL", "Biological"
        ADOPTIVE = "ADOPTIVE", "Adoptive"
        STEP = "STEP", "Step"
        FOSTER = "FOSTER", "Foster"
        UNKNOWN = "UNKNOWN", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="relationships",
        db_index=True,
    )
    person_a = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="relationships_as_subject",
        db_index=True,
    )
    person_b = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="relationships_as_target",
        db_index=True,
    )
    relationship_type = models.CharField(
        max_length=30,
        choices=Type.choices,
        db_index=True,
    )
    relationship_subtype = models.CharField(
        max_length=30,
        choices=Subtype.choices,
        default=Subtype.BIOLOGICAL,
    )
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Relationship"
        verbose_name_plural = "Relationships"
        unique_together = ("family", "person_a", "person_b", "relationship_type", "relationship_subtype")
        indexes = [
            models.Index(fields=["family", "person_a", "relationship_type"]),
            models.Index(fields=["family", "person_b", "relationship_type"]),
        ]

    def __str__(self):
        return f"{self.person_a.full_name} -> {self.person_b.full_name} ({self.relationship_type})"

    def clean(self):
        if self.person_a_id == self.person_b_id:
            raise ValidationError("A person cannot have a relationship with themselves.")
        if self.person_a.family_id != self.person_b.family_id:
            raise ValidationError("Both individuals must belong to the same family.")


class MarriagePartnership(models.Model):
    """
    First-class model for marital and domestic partnerships between two individuals.
    Allows modeling multiple marriages across time, divorces, and widowhood.
    """
    class PartnershipType(models.TextChoices):
        MARRIAGE = "MARRIAGE", "Marriage"
        CIVIL_UNION = "CIVIL_UNION", "Civil Union"
        DOMESTIC_PARTNERSHIP = "DOMESTIC_PARTNERSHIP", "Domestic Partnership"

    class EndReason(models.TextChoices):
        ONGOING = "ONGOING", "Ongoing"
        DEATH = "DEATH", "Death of Spouse"
        DIVORCE = "DIVORCE", "Divorce"
        ANNULMENT = "ANNULMENT", "Annulment"
        SEPARATION = "SEPARATION", "Separation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="marriages",
        db_index=True,
    )
    partner_1 = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="marriages_as_p1",
    )
    partner_2 = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="marriages_as_p2",
    )
    partnership_type = models.CharField(
        max_length=30,
        choices=PartnershipType.choices,
        default=PartnershipType.MARRIAGE,
    )
    start_date = models.DateField(null=True, blank=True)
    start_place = models.CharField(max_length=255, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_reason = models.CharField(
        max_length=30,
        choices=EndReason.choices,
        default=EndReason.ONGOING,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marriage / Partnership"
        verbose_name_plural = "Marriages & Partnerships"

    def __str__(self):
        return f"{self.partner_1.full_name} & {self.partner_2.full_name} ({self.end_reason})"

    def clean(self):
        if self.partner_1_id == self.partner_2_id:
            raise ValidationError("A person cannot enter a partnership with themselves.")
        if self.partner_1.family_id != self.partner_2.family_id:
            raise ValidationError("Both partners must belong to the same family.")
