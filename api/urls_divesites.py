# -----------------------------------------------------------------------------
# api/url_divesitess.py
#
# This is the url resolver for the actual logbook. 
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url (r'^$', 'api.views.sites.external'),
    url (r'^([0-9A-Fa-f-]{32,36})$', 'api.views.sites.external'),
)
