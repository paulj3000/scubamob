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


urlpatterns = [
    path('', divesites_views.IndexView.as_view(), name='divesites_home'),
    re_path(r'(?P<url>[\w-]*)$', divesites_views.SiteView.as_view(), name="site"),
]
