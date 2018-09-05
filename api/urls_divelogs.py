# -----------------------------------------------------------------------------
# api/url_divelogs.py
#
# This is the url resolver for the actual logbook. 
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url (r'^$', 'api.views.logs.external', name='external_list_shortcut'),
    url (r'^([0-9A-Fa-f-]{20,30})$', 'api.views.logs.external', name='external_logs'),
#    url (r'^(.*)$', 'api.views.invalid'),
)
