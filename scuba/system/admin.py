from django.contrib import admin
from django.utils.safestring import mark_safe

import scuba.system.models as system_models
from scuba.settings import AWS_CLOUDFRONT_DEPLOY


class CodeBuildJobAdminInline(admin.TabularInline):
    """ CodeBuildJob
    """
    fields = ('build_status', 'branch', 'start_time', 'end_time', 'reports',)
    readonly_fields = ('reports', 'branch', 'build_status', 'start_time', 'end_time',)

    model = system_models.CodeBuildJob
    extra = 0
    max_num = 0

    def reports(self, obj):
        if not obj.is_completed:
            return 'Not available yet'

        base_url = f"{AWS_CLOUDFRONT_DEPLOY}builds/"
        url = f'<a target="_blank" href="{base_url}{obj.id}/coverage/">Coverage</a> | ' + \
              f'<a target="_blank" href="{base_url}{obj.id}/flake-report/">Flake8</a>'

        return mark_safe(url)


class CodeBuildProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'last_successful_build',)

    inlines = [
        CodeBuildJobAdminInline,
    ]


class CodePipelineStateAdminInline(admin.TabularInline):
    """ CodePipelineStateAdminInline
    """
    model = system_models.CodePipelineState
    extra = 0
    max_num = 0


class CodePipelineProjectAdmin(admin.ModelAdmin):
    list_display = ('pipeline',)

    inlines = [
        CodePipelineStateAdminInline,
    ]


class CodePipelineStateAdmin(admin.ModelAdmin):
    list_display = ('pipeline', 'state',)


admin.site.register(system_models.CodeBuildProject, CodeBuildProjectAdmin)
admin.site.register(system_models.CodePipelineProject, CodePipelineProjectAdmin)
admin.site.register(system_models.CodePipelineState, CodePipelineStateAdmin)
