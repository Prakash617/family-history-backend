from django.db import transaction
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Family, FamilyMembership
from .permissions import IsFamilyAdmin, IsFamilyOwner, IsFamilyViewerOrPublic
from .serializers import (
    FamilyDashboardStatsSerializer,
    FamilyMembershipSerializer,
    FamilySerializer,
)


class FamilyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Family tenants.
    """
    serializer_class = FamilySerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Family.objects.filter(privacy=Family.Privacy.PUBLIC).annotate(
                members_count=Count("members", distinct=True)
            )

        return (
            Family.objects.filter(
                Q(memberships__user=user) | Q(privacy=Family.Privacy.PUBLIC)
            )
            .distinct()
            .annotate(members_count=Count("members", distinct=True))
        )

    def get_permissions(self):
        if self.action in ["list", "retrieve", "dashboard"]:
            return [permissions.AllowAny() if self.action != "dashboard" else permissions.IsAuthenticated()]
        if self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsFamilyAdmin()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsFamilyOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        with transaction.atomic():
            family = serializer.save(owner=self.request.user)
            FamilyMembership.objects.create(
                family=family,
                user=self.request.user,
                role=FamilyMembership.Role.OWNER,
            )

    @extend_schema(responses={200: FamilyDashboardStatsSerializer})
    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated, IsFamilyViewerOrPublic])
    def dashboard(self, request, pk=None):
        family = self.get_object()
        members = family.members.all()
        total_members = members.count()
        living_members = members.filter(is_living=True).count()
        deceased_members = total_members - living_members

        total_photos = family.media.filter(media_type="PHOTO").count() if hasattr(family, "media") else 0
        total_stories = family.stories.filter(status="PUBLISHED").count() if hasattr(family, "stories") else 0
        total_relationships = family.relationships.count() if hasattr(family, "relationships") else 0

        recent_activity = []
        recent_members = members.order_by("-created_at")[:5]
        for m in recent_members:
            recent_activity.append({
                "type": "MEMBER_ADDED",
                "title": f"Added {m.full_name}",
                "timestamp": m.created_at,
                "id": str(m.id),
            })

        data = {
            "total_members": total_members,
            "living_members": living_members,
            "deceased_members": deceased_members,
            "total_photos": total_photos,
            "total_stories": total_stories,
            "total_relationships": total_relationships,
            "recent_activity": recent_activity,
        }
        return Response(data)


class FamilyMembershipViewSet(viewsets.ModelViewSet):
    """
    Manage user memberships within a specific family.
    """
    serializer_class = FamilyMembershipSerializer

    def get_queryset(self):
        family_id = self.kwargs.get("family_pk")
        user = self.request.user
        if not user.is_authenticated:
            return FamilyMembership.objects.none()

        return FamilyMembership.objects.filter(
            family_id=family_id,
            family__memberships__user=user,
        ).select_related("user", "family")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated(), IsFamilyViewerOrPublic()]
        return [permissions.IsAuthenticated(), IsFamilyAdmin()]

    def perform_create(self, serializer):
        family = Family.objects.get(pk=self.kwargs.get("family_pk"))
        serializer.save(family=family)
