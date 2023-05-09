from django.db import models
from django.templatetags.static import static

from scuba.libs.models.uuidmodel import UUIDModel


class Diveshop(UUIDModel):
    name = models.CharField(max_length=100)

'''
    description = models.TextField()
    url = models.URLField(max_length=255, db_index=True, blank=True)
    lat = models.DecimalField(max_digits=15, decimal_places=9)
    long = models.DecimalField(max_digits=15, decimal_places=9)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'diveshop'

    def __str__(self):
        return self.name

    @staticmethod
    def get_local_diveshops(lon, lat, radius):
        return Diveshop.objects.filter(is_active=True)
'''
