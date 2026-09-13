from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PersonViewSet

router = DefaultRouter()
router.register(r"people", PersonViewSet, basename="person")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "families/<uuid:family_pk>/people/",
        PersonViewSet.as_view({"get": "list", "post": "create"}),
        name="family-people-list",
    ),
]
