import datetime
import time
import random
import uuid

from django.db import models


class Logbook(models.Model):
    user = models.ForeignKey('accounts.User', related_name='logbooks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=144)

    class Meta:
        db_table = 'logbook'
        unique_together = (('user', 'name'), )

    @staticmethod
    def get_logs(user):
        pass


class LogbookFolder(models.Model):
    user = models.ForeignKey(User, related_name='logbook_folders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def init_guid(self):
        return str(uuid.uuid1()).replace('-', '')

    def get_logs(self):
        divelog_mongo = DiveLog()
        return divelog_mongo.get_log(user_id=self.user.id, folder=self.guid)

    class Meta:
        db_table = 'logbook_folder'
        unique_together = (('user', 'name'), )


class LogbookTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guid = models.CharField(max_length=40)
    name = models.CharField(max_length=255)

    def init_guid(self):
        return str(uuid.uuid1()).replace('-', '')

    def save(self, *args, **kwargs):
        # make sure we have a valid guid
        self.guid = self.init_guid() if not self.guid else self.guid

        # save the object
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'logbook_tag'
        unique_together = (('user', 'name'), )
