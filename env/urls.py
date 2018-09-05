# -----------------------------------------------------------------------------
# env/urls.py
#
# This is the urls.py for all things environmental related
#
# (C) Copyright 2013, Digital Infinity Software.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.conf.urls import patterns, url
from django.contrib.auth.views import password_reset
from django.views.generic import TemplateView

urlpatterns = patterns('',
    ## let's start some stuff on environmental issues
    (r'^env/sharks/$',        TemplateView.as_view(template_name="env/sharks.html")),
    (r'^env/science_exchange/$',        TemplateView.as_view(template_name="env/science_exchange.html")),
)
