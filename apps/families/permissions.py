from rest_framework import permissions

from .models import Family, FamilyMembership


class HasFamilyRole(permissions.BasePermission):
    """
    Checks if the user has at least the required role in the family.
    Hierarchy: OWNER > ADMIN > EDITOR > VIEWER
    """
    ROLE_HIERARCHY = {
        FamilyMembership.Role.OWNER: 4,
        FamilyMembership.Role.ADMIN: 3,
        FamilyMembership.Role.EDITOR: 2,
        FamilyMembership.Role.VIEWER: 1,
    }

    required_role = FamilyMembership.Role.VIEWER

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            # Allow safe methods if family is PUBLIC
            if request.method in permissions.SAFE_METHODS:
                family = obj if isinstance(obj, Family) else getattr(obj, "family", None)
                if family and family.privacy == Family.Privacy.PUBLIC:
                    return True
            return False

        if request.user.is_superuser:
            return True

        family = obj if isinstance(obj, Family) else getattr(obj, "family", None)
        if not family:
            return False

        try:
            membership = FamilyMembership.objects.get(family=family, user=request.user)
            user_level = self.ROLE_HIERARCHY.get(membership.role, 0)
            required_level = self.ROLE_HIERARCHY.get(self.required_role, 1)
            return user_level >= required_level
        except FamilyMembership.DoesNotExist:
            if request.method in permissions.SAFE_METHODS and family.privacy == Family.Privacy.PUBLIC:
                return True
            return False


class IsFamilyViewerOrPublic(HasFamilyRole):
    required_role = FamilyMembership.Role.VIEWER


class IsFamilyEditor(HasFamilyRole):
    required_role = FamilyMembership.Role.EDITOR


class IsFamilyAdmin(HasFamilyRole):
    required_role = FamilyMembership.Role.ADMIN


class IsFamilyOwner(HasFamilyRole):
    required_role = FamilyMembership.Role.OWNER
