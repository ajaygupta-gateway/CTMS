from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
import pytz

class TaskAccessPermission(BasePermission):
    """
    Handles role-based + time-based access control for tasks.
    """
    #object level permission = Object-level permission = permission that is checked for a specific database object. "Can THIS user access THIS task?"
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Everyone can READ
        if request.method in SAFE_METHODS:  #SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
            return True

        #Now this covers all requests other than safe method

        # Auditors can never WRITE
        if user.is_auditor():
            return False

        # Managers have no restrictions
        if user.is_manager():
            return True

        # Developers logic
        if user.is_developer():
            # Critical tasks can be updated anytime
            if obj.priority == "critical":
                return True

            # Time-based restriction
            user_tz = pytz.timezone(user.timezone)  #Converts the user’s timezone string (e.g. "Asia/Kolkata") Into a timezone object
            now_local = timezone.now().astimezone(user_tz)
            """
            timezone.now() → current UTC time
            .astimezone(user_tz) → converts to user’s local time
            
            Now you know:
                “What time is it for THIS user?”
            """

            start_hour = 9
            end_hour = 18

            return start_hour <= now_local.hour < end_hour

        return False #deny by default

class TaskCreatePermission(BasePermission):
    """
    Controls who can create tasks.

    has_permission:
    Called before any object exists

    Used for: POST (create), List views, Bulk operations
    """

    def has_permission(self, request, view):
        if request.method != "POST":
            return True

        user = request.user

        if user.is_manager():
            return True

        if user.is_developer():
            user_tz = pytz.timezone(user.timezone)  # Converts the user’s timezone string (e.g. "Asia/Kolkata") Into a timezone object
            now_local = timezone.now().astimezone(user_tz)

            start_hour = 9
            end_hour = 18

            # Developers can create tasks only for themselves
            assigned_to = request.data.get("assigned_to")  # Reads the assigned_to field from POST body

            return start_hour <= now_local.hour < end_hour and str(user.id) == str(assigned_to)

        return False #     Deny for: Auditors, Unknown roles, Malformed requests
