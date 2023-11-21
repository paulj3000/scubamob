"""
scuba/galleries/admin.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

The admin page for the galleries app
"""
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib import admin

import scuba.galleries.models as galleries_models


admin.site.register(galleries_models.Album)
