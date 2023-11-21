from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel


# Create your models here.
class SearchLocation(UUIDModel):
    user = models.ForeignKey(
            'accounts.User',
            related_name='search_locations',
            on_delete=models.CASCADE)

    location = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'search_location'
