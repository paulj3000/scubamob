import uuid

from django.db import models


class UUIDModel(models.Model):
    ''' replace the primary key with a uuid field '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    @property
    def pk_as_str(self):
        return str(self.id).replace('-', '')
