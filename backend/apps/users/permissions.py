from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager()


class IsDeveloper(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_developer()


class IsAuditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_auditor()


class AuditorReadOnly(BasePermission):
    """
    Auditors can only READ.
    WRITE attempts must return 403.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_auditor():
            return request.method in SAFE_METHODS

        return True




class UserAccessPermission(BasePermission):
    """
    Controls who can view user data.
    """

    def has_permission(self, request, view):
        # Allow list + me for authenticated users
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method not in SAFE_METHODS:
            return False

        if obj == user:
            return True

        if user.is_auditor():
            return True

        if user.is_manager() and obj.is_developer():
            return True

        return False

