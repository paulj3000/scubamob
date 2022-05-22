"""
skm/home/admin.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

The admin page for the home app
"""
from __future__ import unicode_literals

from django.contrib import admin
from scuba.home.forms.admin import JumbotronForm
from scuba.home.models import Jumbotron


class JumbotronAdmin(admin.ModelAdmin):
    """ HomeDemoAdmin

    Override some of the display elements for the admin display
    """
    form = JumbotronForm


admin.site.register(Jumbotron, JumbotronAdmin)
