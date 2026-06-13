from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Only admin role."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrStaff(permissions.BasePermission):
    """Admin or staff role."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'staff')


class IsOwnerOrAdmin(permissions.BasePermission):
    """Owner of the object OR admin."""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        return obj.id == request.user.id
