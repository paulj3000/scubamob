# -----------------------------------------------------------------------------
# logbook/urls.py
#
# This is the url resolver for the actual logbook. 
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'initdev/([0-9A-Fa-f]{20,36})$', 'api.views.mobileapp.initdevice'),
    url(r'mauth/([0-9A-Fa-f]{20,36})$', 'api.views.mobileapp.mauth'),
    url(r'login/([0-9A-Fa-f]{20,36})$', 'api.views.mobileapp.login'),
)
