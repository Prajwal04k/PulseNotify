from rest_framework import permissions
from .models import UserProfile


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to users with role = ADMIN
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.profile.role == UserProfile.Role.ADMIN
