from django.db import models
from django.core.cache import cache

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.weather import Weather


class Region(UUIDModel):
    name = models.CharField(max_length=10)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        db_table = 'regions'
        unique_together = (('name', 'region', 'country'), )

    def __str__(self):
        return f"{self.name}, {self.region}  {self.country}"

    @staticmethod
    def store_weather_region(weather_json):
        from pprint import pprint
        pprint(weather_json)
        location = weather_json['location']

        obj, _ = Region.objects.get_or_create(
            name=location['name'].upper(),
            region=location['region'].upper(),
            country=location['country'].upper())

        return obj

    @staticmethod
    def xget_weather_by_lat_long(lat, long):
        from pprint import pprint
        pprint(weather_json)

        location = weather_json['location']
        key = f'weather_{obj.pk_as_str}'
        weather = cache.get(key, 3600)

        obj, _ = Region.objects.get_or_create(
            name=location['name'].upper(),
            region=location['region'].upper(),
            country=location['country'].upper())

        return obj

    @staticmethod
    def get_weather_by_lat_long(lat, long):
        weather_json = Weather.get_current_by_lat_lng(lat, long)
        region = Region.store_weather_region(weather_json)

        return weather_json, region
