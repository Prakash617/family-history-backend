from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.families.models import FamilyMembership

from .models import Invitation
from .serializers import AcceptInvitationSerializer, InvitationSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationSerializer

    def get_queryset(self):
        family_id = self.request.query_params.get("family")
        qs = Invitation.objects.all().select_related("family", "invited_by")
        if family_id:
            qs = qs.filter(family_id=family_id)
        return qs

    def get_permissions(self):
        return [permissions.IsAuthenticated()]


class AcceptInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = serializer.invitation

        # Add user to family
        membership, created = FamilyMembership.objects.update_or_create(
            family=invite.family,
            user=request.user,
            defaults={"role": invite.role},
        )
        invite.status = Invitation.Status.ACCEPTED
        invite.save()

        return Response(
            {"detail": f"Successfully joined {invite.family.name} as {invite.role}.", "family_id": str(invite.family.id)},
            status=status.HTTP_200_OK,
        )
