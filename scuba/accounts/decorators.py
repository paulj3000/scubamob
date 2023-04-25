from django.http import Http404
from django.shortcuts import get_object_or_404

from scuba.accounts.models import User


def can_view_profile(view_func):
    """Decorator makes sure the user is a premium user"""
    def _wrapped_view_func(request, *args, **kwargs):
        """ Wrapper for the function

        Check of the user is allowed to access this profile
        """
        # simple check. are there programs available?
        user = request.user
        id = kwargs.get('id')

        if user.pk_as_str == id:
            # that's this user. he's obviously cleared
            setattr(request, 'is_user', True)
            setattr(request, 'profile', user)
            return view_func(request, *args, **kwargs)

        # check if this is a valid profile
        profile_user = get_object_or_404(User, id=id)

        if user.is_blocked(profile_user):
            raise Http404

        if not profile_user.is_active:
            raise http404

        if profile_user.is_private:
            raise http404

        setattr(request, 'profile', profile_user)
        setattr(request, 'is_user', False)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
