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

import scuba.diveshops.views as diveshops_views
import scuba.diveshops.views as diveshops_shopadmin


urlpatterns = [
    path('', diveshops_views.index, name="diveshops_home"),
    '''
    path('create_site/', diveshops_shopadmin.packages, name="diveshops_packages"),
    path('new/', diveshops_shopadmin.editshop, name="diveshops_new"),
    '''

    path('json/getlocaldiveshops/', diveshops_views.getlocaldiveshops),
]
