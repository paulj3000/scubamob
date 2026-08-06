from rest_framework import permissions

from scuba.accounts.models import User


class CanViewProfile(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        # get the user object
        user = request.user

        # get the profile id comign in
        id = view.kwargs.get('id')

        obj = User.objects.filter(id=id).first()
        if not obj:
            return False

        # make sure neither user has blocked the other
        if user.is_blocked(obj):
            return False

        return True
