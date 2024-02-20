from django.db import models


class InvalidCodebuildException(Exception):
    pass


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
    project = models.CharField(max_length=128)
    logs = models.CharField(max_length=256)
    branch = models.CharField(max_length=256)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'codebuild_job'
