from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel


class LocationModel(UUIDModel):
    ''' replace the primary key with a uuid field '''
    name = models.CharField(max_length=128)
    lat = models.FloatField(default=0.0)
    lng = models.FloatField(default=0.0)
    url = models.CharField(max_length=255, blank=True, unique=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        """ return a string representation of the model """
        return self.name

    @classmethod
    def generate_url(cls, name):
        url = StringUtils.generate_url_from_string(name)
        retval = url

        extra = 1   # create an "extra" variable to update
        while cls.objects.filter(url=retval).count():
            retval = f"{url}-{extra}"
            extra += 1

        return retval

    @classmethod
    def get_local_objects(cls, lat, lng, distance, **kwargs):
        lat = float(lat)
        lng = float(lng)

        # Haversine formula = https://en.wikipedia.org/wiki/Haversine_formula
        R = 6378.1  # earth radius
        bearing = 1.57  # 90 degrees bearing converted to radians.

        lat1 = math.radians(lat)  # lat in radians
        lngg1 = math.radians(lng)  # lngg in radians

        lat2 = math.asin(math.sin(lat1) * math.cos(distance / R)
                         + math.cos(lat1) * math.sin(distance / R)
                         * math.cos(bearing))

        lngg2 = lngg1 + math.atan2(
            math.sin(bearing) * math.sin(distance/R) * math.cos(lat1),
            math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))

        lat2 = math.degrees(lat2)
        lngg2 = math.degrees(lngg2)

        return cls.objects.filter(
            current_lat__gte=lat1, current_lat__lte=lat2).filter(
                current_lngg__gte=lngg1, current_lngg__lte=lngg2)
