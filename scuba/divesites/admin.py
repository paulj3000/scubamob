# -*- coding: utf-8 -*-
from django.contrib import admin

import scuba.divesites.models as divesites_models


class DivesiteAdmin(admin.ModelAdmin):
    readonly_fields = ['url']


admin.site.register(divesites_models.Divesite, DivesiteAdmin)
