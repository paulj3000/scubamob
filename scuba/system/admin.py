from django.contrib import admin

import scuba.system.models as system_models


class CodeBuildJobAdminInline(admin.StackedInline):
    """ CodeBuildJob
    """
    model = system_models.CodebuildJob
    extra = 0


class CodeBuildProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'last_successful_build',)

    inlines = [
        CodeBuildJobAdminInline,
    ]


admin.site.register(system_models.CodebuildProject, CodeBuildProjectAdmin)
