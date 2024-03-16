from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel


class InvalidCodebuildException(Exception):
    pass


class CodebuildProject(models.Model):
    ''' replace the primary key with a uuid field '''
    id = models.CharField(max_length=128, primary_key=True, editable=False)
    project = models.CharField(max_length=128)
    last_successful_build = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """ return a string representation of the model """
        return self.project

    class Meta:
        db_table = 'codebuild_project'


class CodebuildJob(models.Model):
    ''' replace the primary key with a uuid field '''

    BUILD_STATUS_VALUES = {
        (0, 'IN_PROGRESS'),
        (1, 'SUCCEEDED'),
        (2, 'FAILED'),
        (3, 'STOPPED'),
    }

    id = models.CharField(max_length=128, primary_key=True, editable=False)
    build_status = models.PositiveSmallIntegerField(choices=BUILD_STATUS_VALUES, default=0)
    project = models.ForeignKey(CodebuildProject, related_name='jobs', on_delete=models.CASCADE)
    logs = models.CharField(max_length=256)
    branch = models.CharField(max_length=256)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        get_latest_by = "-end_time"
        db_table = 'codebuild_job'
