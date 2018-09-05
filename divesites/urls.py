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
    url(r'^$', 'divesites.views.index',name="divesites_home"),
    url(r'^edit/([0-9A-Fa-f]{20,36})?$', 'divesites.views.newsite',name="divesites_new"),
    url(r'^json/locations/?$', 'divesites.views.json.getdivesites'),
    url(r'^json/getdivesiteinfo/([0-9A-Fa-f]{20,36})/?$', 'divesites.views.json.getdivesiteinfo'),
)
