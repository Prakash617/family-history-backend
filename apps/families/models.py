import uuid

from django.conf import settings
from django.db import models


class Family(models.Model):
    """
    Family tenant container representing a genealogical family line.
    """
    class Privacy(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        PRIVATE = "PRIVATE", "Private"
        INVITE_ONLY = "INVITE_ONLY", "Invite Only"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="family_covers/", null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_families",
    )
    privacy = models.CharField(
        max_length=20,
        choices=Privacy.choices,
        default=Privacy.PRIVATE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class FamilyMembership(models.Model):
    """
    Associates a system user with a family and grants a specific role.
    """
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        EDITOR = "EDITOR", "Editor"
        VIEWER = "VIEWER", "Viewer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
    )
    # User can optionally be linked to a person node inside the family tree
    linked_person = models.ForeignKey(
        "members.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_user_memberships",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Family Membership"
        verbose_name_plural = "Family Memberships"
        unique_together = ("family", "user")
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.email} - {self.family.name} ({self.role})"
