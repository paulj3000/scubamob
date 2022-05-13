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

import api.views.mobile_account as api_mobile_account


urlpatterns = [
    path('', api_mobile_account.external),
    re_path(r'^([\w]{5,36})$', api_mobile_account.external),
]
