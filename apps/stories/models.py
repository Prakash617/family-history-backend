import uuid

from django.conf import settings
from django.db import models

from apps.families.models import Family
from apps.members.models import Person


class Story(models.Model):
    """
    Narrative historical story or memory associated with family and ancestors.
    """
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        ARCHIVED = "ARCHIVED", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="stories", db_index=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stories")
    title = models.CharField(max_length=255)
    content = models.TextField()
    cover_image = models.ImageField(upload_to="story_covers/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED, db_index=True)
    associated_people = models.ManyToManyField(Person, blank=True, related_name="stories")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
