# -----------------------------------------------------------------------------
# logbook/urls.py
#
# This is the url resolver for the actual logbook.
#
# (C) Copyright 2013, Scubalog.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.urls import path

import scuba.diveshops.views as diveshops_views


urlpatterns = [
    path('', diveshops_views.index, name="diveshops_home"),
    path('json/getlocaldiveshops/', diveshops_views.getlocaldiveshops),
]

'''
path('create_site/', diveshops_shopadmin.packages, name="diveshops_packages"),
path('new/', diveshops_shopadmin.editshop, name="diveshops_new"),
'''
