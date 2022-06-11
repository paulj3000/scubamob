from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel


class Divesite(UUIDModel):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=255)

    class Meta:
        db_table = 'divesite'
