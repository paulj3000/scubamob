from django.contrib import admin
from django.utils.html import format_html

import scuba.aws.models as aws_models
from scuba.settings import AWS_CLOUDFRONT_DEPLOY


class CodeBuildJobAdminInline(admin.TabularInline):
    """ CodeBuildJob
    """
    fields = ('build_status', 'branch', 'start_time', 'end_time', 'reports',)
    readonly_fields = ('reports', 'branch', 'build_status', 'start_time', 'end_time',)

    model = aws_models.CodeBuildJob
    extra = 0
    max_num = 0

    def reports(self, obj):
        if not obj.is_completed:
            return 'Not available yet'

        base_url = f"{AWS_CLOUDFRONT_DEPLOY}builds/"
        return format_html(
            '<a target="_blank" href="{0}{1}/coverage/">Coverage</a> | '
            '<a target="_blank" href="{0}{1}/flake-report/">Flake8</a>',
            base_url, obj.id)


class CodeBuildProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'last_successful_build',)

    inlines = [
        CodeBuildJobAdminInline,
    ]


class CodePipelineStateAdminInline(admin.TabularInline):
    """ CodePipelineStateAdminInline
    """
    model = aws_models.CodePipelineState
    extra = 0
    max_num = 0


class CodePipelineRunAdmin(admin.ModelAdmin):
    list_display = ('pipeline', 'run_date',)

    inlines = [
        CodePipelineStateAdminInline,
    ]


class CodePipelineStateAdmin(admin.ModelAdmin):
    list_display = ('pipeline', 'state',)


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


admin.site.register(aws_models.CodeBuildProject, CodeBuildProjectAdmin)
admin.site.register(aws_models.CodePipelineRun, CodePipelineRunAdmin)
admin.site.register(aws_models.SNSSubscriptionRequest, SNSSubscriptionRequestAdmin)
