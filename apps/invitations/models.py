import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.families.models import Family


def get_default_expiry():
    return timezone.now() + timedelta(days=7)

def generate_token():
    return secrets.token_urlsafe(32)

class Invitation(models.Model):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EDITOR = "EDITOR", "Editor"
        VIEWER = "VIEWER", "Viewer"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        EXPIRED = "EXPIRED", "Expired"
        REVOKED = "REVOKED", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="invitations", db_index=True)
    email = models.EmailField(db_index=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invitations")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    token = models.CharField(max_length=100, unique=True, default=generate_token)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    expires_at = models.DateTimeField(default=get_default_expiry)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite to {self.email} for {self.family.name} ({self.status})"

    @property
    def is_valid(self):
        return self.status == self.Status.PENDING and timezone.now() < self.expires_at
