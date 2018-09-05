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
    url(r'^$', 'api.views.mobile_account.external'),
    url(r'^/([\w]{5,36})$', 'api.views.mobile_account.external'),
)
