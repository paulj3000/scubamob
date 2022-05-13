# -----------------------------------------------------------------------------
# account/urls.py
#
# This is the urls.py for all things account related
#
# (C) Copyright 2013, Digital Infinity Software.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url, include
from django.contrib.auth.views import password_reset

from account.forms import LoginForm, PasswordForm, SettingsForm

urlpatterns = patterns('',
    url(r'^(?P<username>[0-9A-Za-z]+)/$',  'account.views.profiles.profile', name='user_profile'),
)
