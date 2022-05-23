from django.contrib import admin
from scuba.sitesettings.models import *

class SystemApiAdmin(admin.ModelAdmin):
    list_display = ('key', 'url',)


admin.site.register(SystemApi, SystemApiAdmin)
