from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from .models import Story
from .serializers import StorySerializer


class StoryViewSet(viewsets.ModelViewSet):
    serializer_class = StorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["family", "status", "associated_people"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "published_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        family_id = self.request.query_params.get("family")
        person_id = self.request.query_params.get("person")
        qs = Story.objects.all().select_related("author", "family").prefetch_related("associated_people")

        if family_id:
            qs = qs.filter(family_id=family_id)
        if person_id:
            qs = qs.filter(associated_people__id=person_id)

        return qs.distinct()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
