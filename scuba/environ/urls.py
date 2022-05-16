# -----------------------------------------------------------------------------
# env/urls.py
#
# This is the urls.py for all things environmental related
#
# (C) Copyright 2013, Digital Infinity Software.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.urls import path
from django.views.generic import TemplateView


urlpatterns = [
    # let's start some stuff on environmental issues
    path('env/sharks/', TemplateView.as_view(template_name="env/sharks.html")),
    path('env/science_exchange/', TemplateView.as_view(template_name="env/science_exchange.html")),
]
