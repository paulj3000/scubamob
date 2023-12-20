from django.contrib import admin
from django.contrib import messages

from scuba.sitesettings import models
from scuba.libs.exceptions import ChatServerDownException


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


class GenericKeyValueApiAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_endpoint_form.html'
    list_display = ('key', 'value',)


class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)


class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'value',)


class ApiEndpointAdmin(admin.ModelAdmin):
    list_display = ('app', 'key', 'url',)


class SNSSubscriptionRequestAdmin(admin.ModelAdmin):
    def confirm_sns_request(self, request, queryset):
        for subscription in queryset:
            print(subscription.subscribe_url)

        # set a success message
        # messages.add_message(request, messages.INFO, 'Passwords successfully reset')

    confirm_sns_request.short_description = "Confirm SNS Request"
    actions = [
        confirm_sns_request,
    ]
    list_display = ('topic_arn', 'is_confirmed', 'timestamp',)


admin.site.register(models.ApiEndpoint, ApiEndpointAdmin)
admin.site.register(models.APIKey, APIKeyAdmin)
admin.site.register(models.AlertingApi, GenericKeyValueApiAdmin)
admin.site.register(models.AWSApi, GenericKeyValueApiAdmin)
admin.site.register(models.BillingApi, GenericKeyValueApiAdmin)
admin.site.register(models.ChatApi, GenericKeyValueApiAdmin)
admin.site.register(models.SystemApi, GenericKeyValueApiAdmin)
admin.site.register(models.LogbookApi, GenericKeyValueApiAdmin)
admin.site.register(models.SettingsApi, GenericKeyValueApiAdmin)
admin.site.register(models.FlagOption)
admin.site.register(models.SNSSubscriptionRequest, SNSSubscriptionRequestAdmin)
admin.site.register(models.SystemSetting, SystemSettingAdmin)
