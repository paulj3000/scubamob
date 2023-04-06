import datetime
import time
import random
import uuid

from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel


class Logbook(UUIDModel):
    user = models.ForeignKey('accounts.User', related_name='logbooks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=144)

    class Meta:
        db_table = 'logbook'
        unique_together = (('user', 'name'), )

    @staticmethod
    def get_logs(user):
        pass


class LogbookFolder(UUIDModel):
    user = models.ForeignKey('accounts.User', related_name='logbook_folders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def get_logs(self):
        divelog_mongo = DiveLog()
        return divelog_mongo.get_log(user_id=self.user.id, folder=self.guid)

    class Meta:
        db_table = 'logbook_folder'
        unique_together = (('user', 'name'), )


class LogbookTag(UUIDModel):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'logbook_tag'
        unique_together = (('user', 'name'), )
