from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.families.models import Family
from apps.families.permissions import IsFamilyViewerOrPublic

from .models import MarriagePartnership, Relationship
from .serializers import MarriagePartnershipSerializer, RelationshipSerializer
from .services.tree_engine import TreeEngine


class RelationshipViewSet(viewsets.ModelViewSet):
    """
    Manage genealogical relationships (parent-child, spouse, sibling)
    """
    serializer_class = RelationshipSerializer

    def get_queryset(self):
        family_id = self.request.query_params.get("family")
        qs = Relationship.objects.all().select_related("person_a", "person_b", "family")
        if family_id:
            qs = qs.filter(family_id=family_id)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class MarriagePartnershipViewSet(viewsets.ModelViewSet):
    """
    Manage marriages and domestic partnerships.
    """
    serializer_class = MarriagePartnershipSerializer

    def get_queryset(self):
        family_id = self.request.query_params.get("family")
        qs = MarriagePartnership.objects.all().select_related("partner_1", "partner_2", "family")
        if family_id:
            qs = qs.filter(family_id=family_id)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class FamilyTreeView(APIView):
    """
    Endpoint generating React Flow compatible nodes and edges for tree rendering.
    Supports root person, depth limitation, and traversal direction.
    """
    permission_classes = [IsFamilyViewerOrPublic]

    @extend_schema(
        parameters=[
            OpenApiParameter("root_person_id", str, description="Focus tree on a root person ID"),
            OpenApiParameter("depth", int, description="Generation depth limit (default 4)"),
            OpenApiParameter("direction", str, description="ancestors | descendants | both (default: both)"),
        ],
        responses={200: dict},
    )
    def get(self, request, family_id):
        family = get_object_or_404(Family, pk=family_id)
        self.check_object_permissions(request, family)

        root_person_id = request.query_params.get("root_person_id")
        depth = int(request.query_params.get("depth", 4))
        direction = request.query_params.get("direction", "both")

        engine = TreeEngine(
            family=family,
            root_person_id=root_person_id,
            depth=depth,
            direction=direction,
        )
        data = engine.build_tree()
        return Response(data, status=status.HTTP_200_OK)
