"""
common/permissions.py

Shared DRF permission classes used across all apps.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAdminRole(BasePermission):
    """Allow access only to users whose Role name is 'Admin'."""

    message = "Only Admin users can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name.lower() == "admin"
        )


class IsOrgMember(IsAuthenticated):
    """Allow access only to authenticated users; object-level checks ensure same org."""

    def has_object_permission(self, request, view, obj):
        # obj must have an `organization` attribute
        org = getattr(obj, "organization", None)
        if org is None:
            return False
        return org == request.user.organization


class IsAuditorRole(BasePermission):
    """Allow access only to users with role 'Auditor' or 'Admin'."""

    message = "Only Auditor or Admin users can perform this action."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        role_name = request.user.role.name.lower() if request.user.role else ""
        return role_name in ("admin", "auditor")
