# -----------------------------------------------------------------------------
# logbook/urls.py
#
# This is the url resolver for the actual logbook.
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.urls import path, re_path

import api.views.mobileapp as api_mobileapp


urlpatterns = [
    re_path(r'initdev/([0-9A-Fa-f]{20,36})$', api_mobileapp.initdevice),
    re_path(r'mauth/([0-9A-Fa-f]{20,36})$', api_mobileapp.mauth),
    re_path(r'login/([0-9A-Fa-f]{20,36})$', api_mobileapp.login),
]
