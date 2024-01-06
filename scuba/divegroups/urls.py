# -----------------------------------------------------------------------------
# account/urls.py
#
# This is the urls.py for all things account related
#
# (C) Copyright 2013, Digital Infinity Software.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django.urls import path

import scuba.divegroups.views as friends_views


urlpatterns = [
    path('', friends_views.index, name='friends_index'),
]
