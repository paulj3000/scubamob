from django.contrib import admin

import scuba.maps.models as maps_models


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country')


admin.site.register(maps_models.Region, RegionAdmin)
