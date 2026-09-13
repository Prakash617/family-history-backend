from rest_framework import filters, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Media
from .serializers import MediaSerializer

class MediaViewSet(viewsets.ModelViewSet):
    serializer_class = MediaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["family", "person", "media_type", "visibility"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "captured_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        family_id = self.request.query_params.get("family")
        person_id = self.request.query_params.get("person")
        qs = Media.objects.all().select_related("uploader", "person", "family")

        if family_id:
            qs = qs.filter(family_id=family_id)
        if person_id:
            qs = qs.filter(person_id=person_id)

        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)
