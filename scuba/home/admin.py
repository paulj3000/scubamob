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
    change_form_template = 'home/admin/change_jumbotron_form.html'
    list_display = ('name', 'jumbotron_type', 'is_active',)

    def change_view(self, request, object_id, extra_context=None):
        if object_id:
            self.exclude = ('upload', )

        return super().change_view(request, object_id, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        if obj:
            self.exclude.append('upload')
        return super().get_form(request, obj, **kwargs)


admin.site.register(Jumbotron, JumbotronAdmin)
