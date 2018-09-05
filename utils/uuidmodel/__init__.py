import uuid

from django.db import models

class Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __unicode__(self):
        return "%s(%s)" % (type(self).__name__, self.pk)
    class Meta:
        abstract = True
