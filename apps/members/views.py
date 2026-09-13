from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.families.models import Family
from apps.families.permissions import IsFamilyEditor

from .models import Person
from .serializers import (
    PersonBriefSerializer,
    PersonDetailSerializer,
    PersonSerializer,
)


class PersonViewSet(viewsets.ModelViewSet):
    """
    CRUD and searching for Person entities within a family.
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["gender", "is_living", "privacy", "family"]
    search_fields = ["first_name", "middle_name", "last_name", "preferred_name", "birth_place", "occupation"]
    ordering_fields = ["birth_date", "first_name", "last_name", "created_at"]
    ordering = ["birth_date", "first_name"]

    def get_queryset(self):
        user = self.request.user
        family_id = self.request.query_params.get("family") or self.kwargs.get("family_pk")

        qs = Person.objects.all().select_related("family")

        if not user.is_authenticated:
            qs = qs.filter(family__privacy=Family.Privacy.PUBLIC)
        else:
            qs = qs.filter(
                Q(family__memberships__user=user) | Q(family__privacy=Family.Privacy.PUBLIC)
            ).distinct()

        if family_id:
            qs = qs.filter(family_id=family_id)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PersonDetailSerializer
        if self.action == "list" and self.request.query_params.get("brief") == "true":
            return PersonBriefSerializer
        return PersonSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "relatives"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsFamilyEditor()]

    def perform_create(self, serializer):
        family = serializer.validated_data.get("family")
        self.check_object_permissions(self.request, family)
        serializer.save()

    @action(detail=True, methods=["get"])
    def relatives(self, request, pk=None):
        person = self.get_object()
        serializer = PersonDetailSerializer(person, context={"request": request})
        return Response(serializer.data.get("relatives"))
