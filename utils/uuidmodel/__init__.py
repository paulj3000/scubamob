from django.db import models
from django_extensions.db.fields import UUIDField

class Model(models.Model):
    id = UUIDField(primary_key=True)
    def __unicode__(self):
        return "%s(%s)" % (type(self).__name__, self.pk)
    class Meta:
        abstract = True
