from django.contrib import admin

import scuba.system.models as system_models


class CodeBuildProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'last_successful_build',)


class CodeBuildJobAdmin(admin.ModelAdmin):
    list_display = ('project', 'branch', 'build_status', 'start_time', 'end_time',)


admin.site.register(system_models.CodebuildProject, CodeBuildProjectAdmin)
admin.site.register(system_models.CodebuildJob, CodeBuildJobAdmin)
