from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FamilyMembershipViewSet, FamilyViewSet

router = DefaultRouter()
router.register(r"", FamilyViewSet, basename="family")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<uuid:family_pk>/memberships/",
        FamilyMembershipViewSet.as_view({"get": "list", "post": "create"}),
        name="family-memberships-list",
    ),
    path(
        "<uuid:family_pk>/memberships/<uuid:pk>/",
        FamilyMembershipViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="family-memberships-detail",
    ),
]
