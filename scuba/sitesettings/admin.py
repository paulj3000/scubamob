from django.contrib import admin
from django.contrib import messages

from scuba.sitesettings.models import SystemApi, SystemSetting, DiveLogApi
from scuba.libs.exceptions import ChatServerDownException

class SystemApiAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)

    def sync_settings(self, request, queryset):
        try:
            for setting in queryset:
                setting.sync_settings()

            # set a success message
            messages.add_message(request,
                    messages.INFO, "Settings have been sync'd")
        except ChatServerDownException:
            messages.add_message(request,
                    messages.ERROR, "Cannot connect to chat server")

    sync_settings.short_description = "Sync system apis"

    actions = [
        sync_settings,
    ]


class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)


class DiveLogApiAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)


admin.site.register(SystemApi, SystemApiAdmin)
admin.site.register(DiveLogApi, DiveLogApiAdmin)
admin.site.register(SystemSetting, SystemSettingAdmin)
