# -----------------------------------------------------------------------------
# logbook/urls.py
#
# This is the url resolver for the actual logbook.
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import include
from django.urls import path, re_path

import scuba.logbook.views.dives as dives_views
import scuba.logbook.views.logs_json as logs_json


urlpatterns = [
    path('', dives_views.index, name="logbook_home"),
    path('dives/edit/', dives_views.edit, name="dive_add"),
    re_path(r'^edit/([0-9A-Fa-f]{20,36})/?$', dives_views.edit, name="dive_edit"),

    path('json/logbookfolders', logs_json.logbookfolders),
    path('json/logbookfolderlogs', logs_json.logbookfolderlogs),
]
