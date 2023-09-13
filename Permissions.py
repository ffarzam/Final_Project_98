from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperuser(BasePermission):
    message = 'permission denied, you are not the superuser'

    def has_permission(self, request, view):
        return request.user.is_superuser

