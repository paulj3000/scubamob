from django.shortcuts import get_object_or_404
from rest_framework import permissions

from scuba.accounts.models import User, UserBlocked


class IsUserBlocked(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        id = self.kwargs.get('id')

        profile = User.objects.filter(id=id).first()
        if not profile:
            return False

        ip_addr = request.META['REMOTE_ADDR']
        blocked = Blocklist.objects.filter(ip_addr=ip_addr).exists()
        return not blocked


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

        # make sure the user can see the permission
        if user.blocked.filter(buddy=obj) or obj.blocked.filter(user=obj):
            return False

        return True
