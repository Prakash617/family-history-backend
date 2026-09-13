import uuid

from django.db import models

from apps.families.models import Family
from apps.members.models import Person


class Event(models.Model):
    """
    Chronological milestone or historical event in a person or family's timeline.
    """
    class EventType(models.TextChoices):
        BIRTH = "BIRTH", "Birth"
        MARRIAGE = "MARRIAGE", "Marriage"
        DEATH = "DEATH", "Death"
        EDUCATION = "EDUCATION", "Education / Graduation"
        MIGRATION = "MIGRATION", "Migration / Relocation"
        CAREER = "CAREER", "Career / Business"
        RESIDENCE = "RESIDENCE", "Residence"
        MILITARY = "MILITARY", "Military Service"
        OTHER = "OTHER", "Other Milestone"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="events", db_index=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name="events")
    event_type = models.CharField(max_length=30, choices=EventType.choices, default=EventType.OTHER, db_index=True)
    title = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    date_text = models.CharField(max_length=100, blank=True, help_text="Textual representation like 'Spring 1968'")
    place = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["date", "created_at"]

    def __str__(self):
        return f"{self.title} ({self.event_type})"
