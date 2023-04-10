from django.db import models
from django.db import connection

from scuba.libs.exceptions import InvalidWeatherDataException
from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.external.google_address import GoogleAddress
from scuba.sitesettings.models import APIKey
from scuba.weather.libs.weather import Weather as WeatherAPI


class Weather(UUIDModel):
    """ Weather

    Store weather in the database. Will make it easier to
    query based on latitude and longitude by way of
    haversine functions
    """
    name = models.CharField(max_length=128)
    region = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    lat = models.DecimalField(max_digits=15, decimal_places=9)
    lng = models.DecimalField(max_digits=15, decimal_places=9)
    tz_id = models.CharField(max_length=64)
    localtime = models.PositiveIntegerField()
    data = models.JSONField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'weather'

    def __str__(self):
        """ return a string representation of the model """
        return f"{self.name}, {self.region}  {self.country}"

    @staticmethod
    def get_current_by_postal_code(postal_code, distance=100):
        result = GoogleAddress.get_geocode_from_postal_code(postal_code)
        location = result[0]['geometry']['location']

        return Weather.get_current_by_lat_lng(location['lat'], location['lng'], distance)

    @staticmethod
    def get_current_by_lat_lng(lat, lng, distance=100):
        """ get_current_by_lat_lng

        query the database by way of haverine and get
        requested data. If it does not exist, call the weather API
        interface, store it, then return it
        """
        RADIUS_MILES = 3959
        sql = f"""SELECT id, ( {RADIUS_MILES} * acos( cos( radians(%s) ) * cos( radians( lat ) )
        * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin(radians(lat)) ) )
        AS distance FROM weather WHERE distance < %s
        ORDER BY distance
        LIMIT 0 , 20"""

        weather = Weather.objects.raw(sql, [lat, lng, lat, distance])
        if len(weather):
            return weather

        new_weather = WeatherAPI.get_current_by_lat_lng(lat, lon)
        Weather.add_weather_data(new_weather)

        return new_weather

    @staticmethod
    def add_weather_data(data):
        """ add_weather_data

        store the incoming json data into the database
        """
        try:
            location = data['location']
            return Weather.objects.create(
                name=location['name'],
                region=location['region'],
                country=location['country'],
                lat=location['lat'],
                lng=location['lon'],
                tz_id=location['tz_id'],
                localtime=location['localtime_epoch'],
                data=data)
        except KeyError as e:
            raise InvalidWeatherDataException(str(e))
