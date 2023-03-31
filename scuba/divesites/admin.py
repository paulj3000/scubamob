# -*- coding: utf-8 -*-
from django.contrib import admin

import scuba.divesites.models as divesites_models


admin.site.register(divesites_models.Divesite)
