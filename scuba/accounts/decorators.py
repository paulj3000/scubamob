from django.http import Http404
from django.shortcuts import get_object_or_404

from scuba.accounts.models import User


def can_view_profile(view_func):
    """Decorator makes sure the user is a premium user"""
    def _wrapped_view_func(request, *args, **kwargs):
        """ Wrapper for the function

        Get the profile by way of the username coming in
        Check of the user is allowed to access this profile
        """
        user = request.user
        username = kwargs.get('username')

        # get the profile first, make sure it actually exists
        profile = get_object_or_404(User, username=username)

        if user.pk_as_str == profile.pk_as_str:
            # that's this user. he's obviously cleared
            setattr(request, 'is_user', True)
            setattr(request, 'profile', user)
            return view_func(request, *args, **kwargs)

        if user.is_blocked(profile) or profile.is_blocked(user):
            raise Http404

        if not profile.is_active:
            raise http404

        if profile.is_private:
            raise http404

        setattr(request, 'profile', profile)
        setattr(request, 'is_user', False)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
