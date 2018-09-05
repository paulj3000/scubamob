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
    url(r'^$', 'logbook.views.dives.index',name="logbook_home"),
    url(r'^dives/edit/$', 'logbook.views.dives.edit',name="dive_add"),
    url(r'^edit/([0-9A-Fa-f]{20,36})/?$', 'logbook.views.dives.edit', name="dive_edit"),
    #url(r'^dives/json/$', 'logbook.views.dives.json'),
    
    url(r'^json/logbookfolders$', 'logbook.views.logs_json.logbookfolders'),
    url(r'^json/logbookfolderlogs$', 'logbook.views.logs_json.logbookfolderlogs'),
)
