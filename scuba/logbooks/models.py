import datetime
import time
import random
import uuid

from django.db import models
from django.db.models.signals import post_save
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from scuba.logbooks.mongo import DiveLog
from scuba.settings import MONGO_DIVELOGS
from scuba.accounts.models import User


class LogbookManager(models.Manager):

    #class Meta:
    #	collection	= MONGO_DIVELOGS

    def get_logs(self, user):
        pass


class Logbook(models.Model):
    user = models.ForeignKey(User, related_name='logbooks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=144)

    class Meta:
        db_table = 'logbook'
        unique_together = (('user', 'name'), )

	#### get our new manager
    objects = LogbookManager()



class LogbookFolder(models.Model):
    user = models.ForeignKey(User, related_name='logbook_folders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def init_guid(self):
        return str(uuid.uuid1()).replace('-','')

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
        return str(uuid.uuid1()).replace('-','')

    def save(self, *args, **kwargs):

        ## make sure we have a valid guid
        self.guid   = self.init_guid() if not self.guid else self.guid

        # save the object
        super(LogbookTag, self).save(*args, **kwargs)

    class Meta:
        db_table = 'logbook_tag'
        unique_together = (('user', 'name'), )

