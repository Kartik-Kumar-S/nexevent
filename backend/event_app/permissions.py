from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizerOrAdminForWrite(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and (
                getattr(request.user, 'role', None) == 2  # organizer
                or getattr(request.user, 'role', None) == 3  # admin
                or request.user.is_staff
                or request.user.is_superuser
            )
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            obj.organizer == request.user
            or getattr(request.user, 'role', None) == 3
            or request.user.is_staff
            or request.user.is_superuser
        )