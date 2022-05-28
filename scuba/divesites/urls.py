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

import scuba.divesites.views as divesites_views
import scuba.divesites.views.json as divesites_json


urlpatterns = [
    path('', divesites_views.index, name="divesites_home"),
    re_path(r'^edit/([0-9A-Fa-f]{20,36})?$', divesites_views.newsite, name="divesites_new"),
    #path('json/locations/', divesites_json.getdivesites),
    #re_path(r'^json/getdivesiteinfo/([0-9A-Fa-f]{20,36})/?$', divesites_json.getdivesiteinfo),
]
