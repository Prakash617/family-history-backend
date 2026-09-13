import uuid
from django.conf import settings
from django.db import models
from apps.families.models import Family
from apps.members.models import Person

class Media(models.Model):
    """
    Photographs, historical documents, certificates, and artifacts.
    """
    class MediaType(models.TextChoices):
        PHOTO = "PHOTO", "Photo"
        DOCUMENT = "DOCUMENT", "Document"
        CERTIFICATE = "CERTIFICATE", "Certificate"
        OTHER = "OTHER", "Other"

    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        FAMILY_ONLY = "FAMILY_ONLY", "Family Only"
        PRIVATE = "PRIVATE", "Private"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="media", db_index=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_media")
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="media_items")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="family_media/")
    media_type = models.CharField(max_length=20, choices=MediaType.choices, default=MediaType.PHOTO)
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    captured_date = models.DateField(null=True, blank=True)
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.FAMILY_ONLY)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Media Item"
        verbose_name_plural = "Media Items"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.media_type})"

    @property
    def url(self):
        return self.file.url if self.file else ""
