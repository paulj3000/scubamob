from math import radians, cos, sin, asin, sqrt

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from scuba.constants import EARTH_RADIUS
from scuba.libs.models.uuidmodel import UUIDModel


class Diveshop(UUIDModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=255, db_index=True, blank=True)
    lat = models.DecimalField(
        max_digits=15, decimal_places=9,
        validators=[MinValueValidator(-90), MaxValueValidator(90)])
    long = models.DecimalField(
        max_digits=15, decimal_places=9,
        validators=[MinValueValidator(-180), MaxValueValidator(180)])
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'diveshop'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(lat__gte=-90) & models.Q(lat__lte=90),
                name='diveshop_lat_in_range'),
            models.CheckConstraint(
                condition=models.Q(long__gte=-180) & models.Q(long__lte=180),
                name='diveshop_long_in_range'),
        ]

    def __str__(self):
        return self.name

    @staticmethod
    def get_local_diveshops(lon, lat, radius):
        """ return active dive shops within `radius` miles of (lat, lon).

        Falls back to all active dive shops when any parameter is missing.
        """
        queryset = Diveshop.objects.filter(is_active=True)

        if lon is None or lat is None or radius is None:
            return queryset

        lat = float(lat)
        lon = float(lon)
        radius = float(radius)

        nearby_ids = [
            shop.id for shop in queryset
            if Diveshop.haversine_distance(lat, lon, float(shop.lat), float(shop.long)) <= radius
        ]

        return queryset.filter(id__in=nearby_ids)

    @staticmethod
    def haversine_distance(lat1, lng1, lat2, lng2):
        """ great-circle distance, in miles, between two lat/lng points """
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
        return 2 * EARTH_RADIUS * asin(sqrt(a))
