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
    url(r'^$', 'diveshops.views.index',name="diveshops_home"),
    url(r'^create_site/?$', 'diveshops.views.shopadmin.packages',name="diveshops_packages"),
    url(r'^new/?$', 'diveshops.views.shopadmin.editshop',name="diveshops_new"),
    
    url(r'^json/getlocaldiveshops/?$', 'diveshops.views.getlocaldiveshops'),
)
