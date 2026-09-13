from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["family", "person", "event_type"]
    search_fields = ["title", "place", "description"]
    ordering_fields = ["date", "created_at"]
    ordering = ["date", "created_at"]

    def get_queryset(self):
        family_id = self.request.query_params.get("family")
        person_id = self.request.query_params.get("person")
        qs = Event.objects.all().select_related("person", "family")

        if family_id:
            qs = qs.filter(family_id=family_id)
        if person_id:
            qs = qs.filter(person_id=person_id)

        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
