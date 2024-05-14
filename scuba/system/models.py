from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel


class InvalidCodeBuildException(Exception):
    pass


class CodeBuildProject(models.Model):
    ''' replace the primary key with a uuid field '''
    id = models.CharField(max_length=128, primary_key=True, editable=False)
    project = models.CharField(max_length=128)
    last_successful_build = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """ return a string representation of the model """
        return self.project

    class Meta:
        db_table = 'codebuild_project'


class CodeBuildJob(models.Model):
    ''' replace the primary key with a uuid field '''

    BUILD_STATUS_VALUES = {
        (0, 'IN_PROGRESS'),
        (1, 'SUCCEEDED'),
        (2, 'FAILED'),
        (3, 'STOPPED'),
    }

    id = models.CharField(max_length=128, primary_key=True, editable=False)
    build_status = models.PositiveSmallIntegerField(choices=BUILD_STATUS_VALUES, default=0)
    project = models.ForeignKey(CodeBuildProject, related_name='jobs', on_delete=models.CASCADE)
    logs = models.CharField(max_length=256)
    branch = models.CharField(max_length=256)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    @property
    def is_completed(self):
        if self.build_status == 1:
            return True

        return False

    class Meta:
        get_latest_by = "-start_time"
        db_table = 'codebuild_job'
        ordering = ("-start_time",)


class CodePipelineProject(models.Model):
    ''' replace the primary key with a uuid field '''
    id = models.CharField(max_length=128, primary_key=True, editable=False)
    pipeline = models.CharField(max_length=128)
    topic_arn = models.CharField(max_length=256)

    def __str__(self):
        """ return a string representation of the model """
        return self.pipeline

    class Meta:
        db_table = 'codepipeline_project'


class CodePipelineState(models.Model):
    ''' replace the primary key with a uuid field '''
    id = models.CharField(max_length=128, primary_key=True, editable=False)
    pipeline = models.ForeignKey(CodePipelineProject, related_name='states', on_delete=models.CASCADE)
    notification_rule_arn = models.CharField(max_length=128)
    state = models.CharField(max_length=64)
    start_time = models.DateTimeField(null=True, blank=True)
    pipeline_execution_attempt = models.PositiveSmallIntegerField(default=0)
    payload = models.CharField(max_length=1024)

    class Meta:
        db_table = 'codepipeline_state'
