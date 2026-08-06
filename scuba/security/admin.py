from django.contrib import admin

# Register your models here.
from scuba.security import models


class ImpersonationEventAdmin(admin.ModelAdmin):
    """ read-only audit log of admin "login as user" support sessions """
    list_display = ('actor', 'target', 'started_at', 'ended_at')
    readonly_fields = ('actor', 'target', 'reason', 'ip_address', 'started_at', 'ended_at')
    search_fields = ('actor__email', 'target__email')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.BlockedCountry)
admin.site.register(models.InvalidSignup)
admin.site.register(models.ImpersonationEvent, ImpersonationEventAdmin)
