# -----------------------------------------------------------------------------
# api/url_divelogs.py
#
# This is the url resolver for the actual logbook.
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.urls import path, re_path

import api.views.logs as api_logs
import api.views as api_views


urlpatterns = [
    path('', api_logs.external, name='external_list_shortcut'),
    re_path(r'^([0-9A-Fa-f-]{20,30})$', api_logs.external, name='external_logs'),
#    url (r'^(.*)$', api_views.invalid),
]
