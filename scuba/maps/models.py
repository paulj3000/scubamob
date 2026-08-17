from django.db import models

from scuba.libs.exceptions import InvalidCoordinatesException
from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.weather import Weather


class Region(UUIDModel):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        db_table = 'regions'
        unique_together = (('name', 'region', 'country'), )

    def __str__(self):
        return f"{self.name}, {self.region}  {self.country}"

    @staticmethod
    def store_weather_region(weather_json):
        location = weather_json['location']

        obj, _ = Region.objects.get_or_create(
            name=location['name'].upper(),
            region=location['region'].upper(),
            country=location['country'].upper())

        return obj

    @staticmethod
    def get_weather_by_lat_long(lat, long):
        try:
            lat_value, long_value = float(lat), float(long)
        except (TypeError, ValueError):
            raise InvalidCoordinatesException()

        if not (-90 <= lat_value <= 90) or not (-180 <= long_value <= 180):
            raise InvalidCoordinatesException()

        weather_json = Weather.get_current_by_lat_lng(lat, long)
        region = Region.store_weather_region(weather_json)

        return weather_json, region
