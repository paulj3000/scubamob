from django.contrib import admin
from django.contrib import messages

from scuba.sitesettings import models
from scuba.libs.exceptions import ChatServerDownException


class EndpointAdminInline(admin.StackedInline):
    """ UserConfirmationCodeAdminInline

    Class representation of the confirmation codes assigned to this user
    """
    model = models.Endpoint
    extra = 0


class SystemApiAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)

    def sync_settings(self, request, queryset):
        try:
            for setting in queryset:
                setting.sync_settings()

            # set a success message
            messages.add_message(
                request,
                messages.INFO, "Settings have been sync'd")

        except ChatServerDownException:
            messages.add_message(
                request,
                messages.ERROR, "Cannot connect to chat server")

    sync_settings.short_description = "Sync system apis"

    actions = [
        sync_settings,
    ]

    inlines = [
        EndpointAdminInline
    ]


class GenericKeyValueApiAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_endpoint_form.html'
    list_display = ('key', 'value',)


class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)


class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)


class EndpointAdmin(admin.ModelAdmin):
    list_display = ('system', 'key', 'url',)


admin.site.register(models.Endpoint, EndpointAdmin)
admin.site.register(models.APIKey, APIKeyAdmin)
admin.site.register(models.AlertingApi, GenericKeyValueApiAdmin)
admin.site.register(models.AWSApi, GenericKeyValueApiAdmin)
admin.site.register(models.BillingApi, GenericKeyValueApiAdmin)
admin.site.register(models.SystemApi, SystemApiAdmin)
admin.site.register(models.SettingsApi, GenericKeyValueApiAdmin)
admin.site.register(models.SystemSetting, SystemSettingAdmin)
