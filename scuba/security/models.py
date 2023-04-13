from django.db import models

from geolite2 import geolite2
from scuba.libs.models.uuidmodel import UUIDModel


class BlockedCountry(UUIDModel):
    """ Log

    Send an alert to specific users
    """
    name = models.CharField(max_length=64,)
    iso = models.CharField(max_length=12, unique=True)

    class Meta:
        db_table = 'blocked_country'
        verbose_name_plural = 'blocked countries'

    def __str__(self):
        return self.name

    @staticmethod
    def is_ip_available(ip_address):
        reader = geolite2.reader()

        match = reader.get(ip_address)
        Log.objects.create(system='GEOIP', message=json.dumps(match))

        if match and 'country' in match:
            return BlockedCountry.objects.filter(iso=match['country']['iso_code']).first(), match['country']['iso_code']

        return None, 'XX'


class InvalidEmail(UUIDModel):
    ''' what page has the user gone to? '''
    email = models.CharField(max_length=128,)
    ip_address = models.CharField(max_length=128, default='0.0.0.0')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'invalid_email'

    def __str__(self):
        """ return a string friendly representation of this model """
        return self.email
