#-----------------------------------------------------------------------------
# utils/middleware/authentication.py
#
# This file adds an extra layer of login for the user.  This will check the
# user against an email address and a password
#
# (C) Copyright 2014, Digital Infinity Sofware.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from scuba.accounts.models import Account
from utils.user_profile import UserProfile


class EmailLogin(object):
    '''
    Authenticate a user based on email.
    '''
    def authenticate(self, email=None, password=None, **kwargs):
        # let's see if we can try to find an email or password
        if email is None:
            email = kwargs.get('email')

            if email is None:
                email = kwargs.get('username')

        if password is None:
            password = kwargs.get('password')

        try:
            # get the user
            user = User.objects.get(email=email)

            # now, check the password.
            if not user.check_password(password):
                user    = None

        # nope, the user does not exist
        except User.DoesNotExist:
            user = None

        return user

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class DefaultBackend(ModelBackend):
    '''
    This is the default backend.  We just want to extend the login
    so we can get some extra functions, basically using the user_profile
    proxy class
    '''
    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return None
