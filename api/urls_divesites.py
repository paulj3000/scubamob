# -----------------------------------------------------------------------------
# api/url_divesitess.py
#
# This is the url resolver for the actual logbook.
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.urls import path, re_path

import api.views.sites as api_sites


urlpatterns = [
    path('', api_sites.external),
    re_path(r'^([0-9A-Fa-f-]{32,36})$', api_sites.external),
]
