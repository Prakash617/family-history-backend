import uuid

from django.db import models

from apps.families.models import Family


class Person(models.Model):
    """
    Represents an individual person within a family tree.
    Decoupled from system User accounts.
    """
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"
        UNKNOWN = "UNKNOWN", "Unknown"

    class Privacy(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        FAMILY_ONLY = "FAMILY_ONLY", "Family Only"
        PRIVATE = "PRIVATE", "Private"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="members",
        db_index=True,
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    preferred_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.UNKNOWN,
    )

    # Date handling: support exact dates and approximate/historical dates
    birth_date = models.DateField(null=True, blank=True)
    birth_year_approx = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. 'circa 1920', '1940s', or approx year",
    )
    birth_place = models.CharField(max_length=255, blank=True)

    death_date = models.DateField(null=True, blank=True)
    death_year_approx = models.CharField(max_length=50, blank=True)
    death_place = models.CharField(max_length=255, blank=True)
    is_living = models.BooleanField(default=True, db_index=True)

    biography = models.TextField(blank=True)
    occupation = models.CharField(max_length=255, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)
    privacy = models.CharField(
        max_length=20,
        choices=Privacy.choices,
        default=Privacy.PUBLIC,
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = ["birth_date", "first_name"]
        indexes = [
            models.Index(fields=["family", "last_name", "first_name"]),
            models.Index(fields=["family", "is_living"]),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        name = " ".join([p for p in parts if p]).strip()
        return name if name else "Unnamed Person"

    @property
    def birth_display(self):
        if self.birth_date:
            return str(self.birth_date.year)
        return self.birth_year_approx or ""

    @property
    def death_display(self):
        if not self.is_living:
            if self.death_date:
                return str(self.death_date.year)
            return self.death_year_approx or "Deceased"
        return ""

    @property
    def lifespan(self):
        b = self.birth_display
        if self.is_living:
            return f"b. {b}" if b else "Living"
        d = self.death_display
        if b or d:
            return f"{b or '?'} – {d or '?'}"
        return "Deceased"
