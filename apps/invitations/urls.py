from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AcceptInvitationView, InvitationViewSet

router = DefaultRouter()
router.register(r"invitations", InvitationViewSet, basename="invitation")

urlpatterns = [
    path("", include(router.urls)),
    path("invitations/accept/", AcceptInvitationView.as_view(), name="invitation-accept"),
]
