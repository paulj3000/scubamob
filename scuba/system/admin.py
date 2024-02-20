from django.contrib import admin

import scuba.system.models as system_models


class CodeBuildJobAdmin(admin.ModelAdmin):
    list_display = ('project', 'build_status', 'start_time', 'end_time',)


admin.site.register(system_models.CodebuildJob, CodeBuildJobAdmin)
