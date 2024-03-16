from django.contrib import admin
from django.utils.safestring import mark_safe

import scuba.system.models as system_models
from scuba.settings import STATIC_URL


class CodeBuildJobAdminInline(admin.TabularInline):
    """ CodeBuildJob
    """
    fields = ('build_status', 'branch', 'start_time', 'end_time', 'coverage', 'flake8')
    readonly_fields = ('reports', 'branch', 'build_status', 'start_time', 'end_time',)

    model = system_models.CodebuildJob
    extra = 0
    max_num = 0

    def coverage(self, obj):
        return mark_safe(f'<a target="_blank" href="{STATIC_URL}{obj.id}/coverage/">Coverage</a>')

    def flake8(self, obj):
        return mark_safe(f'<a target="_blank" href="{STATIC_URL}{obj.id}/flake-report/">Flake8</a>')


class CodeBuildProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'last_successful_build',)

    inlines = [
        CodeBuildJobAdminInline,
    ]


admin.site.register(system_models.CodebuildProject, CodeBuildProjectAdmin)
