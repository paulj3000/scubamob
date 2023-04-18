import logging
import requests

from scuba import settings
from scuba.sitesettings.models import APIKey
from scuba.libs.exceptions import InvalidWeatherDataException


# weatherapi.com settings
WEATHER_API = {
    'current': 'http://api.weatherapi.com/v1/current.json',
    'forecast': 'http://api.weatherapi.com/v1/forecast.json',
}

class Weather:

    @staticmethod
    def get_api_key():
        return APIKey.get_weather_api_key()

    @staticmethod
    def gen_param_lat_lon(lat, lng):
        return f'q={lat},{lng}'

    @staticmethod
    def gen_param_postal(lat, lng):
        return f'q={lat},{lng}'

    @staticmethod
    def get_data_city_state(city, state):
        city = city.replace(' ', '_').lower()
        settings = self.settings
        url = self.settings['url'] % (self.settings['apikey'], state.lower(), city.lower())

        # make the call to weather underground
        data = self.http_interface.invoke(url)

        # ... and of course, let's return the data
        try:
            if str(data['code']) == '200':
                return simplejson.loads(data['response'])
            else:
                raise ValueError("Invalid Response")
        except:
            raise ValueError("Error")


    @classmethod
    def get_current_by_q_param(cls, q_param):
        # call the API and return the data
        res = requests.get(WEATHER_API['current'],
                           {'key': cls.get_api_key(), 'q': q_param})

        if res.status_code >= 400:
            raise InvalidWeatherDataException()

        return res.json()

    @classmethod
    def get_current_by_postal_code(cls, postal_code):
        # call the API and return the data
        res = requests.get(WEATHER_API['current'],
                           {'key': cls.get_api_key(), 'q': postal_code})
        return res.json()

    @classmethod
    def get_current_by_lat_lng(cls, lat, lng):
        res = requests.get(WEATHER_API['current'], {'key': cls.get_api_key(), 'q': f'{lat},{lng}'})

        if res.status_code >= 400:
            raise InvalidWeatherDataException()

        return res.json()

    def parse_data(self, weather_data):
        retval = {}
        retval = weather_data['current_observation']

        try:
            sunrise = weather_data['sun_phase']['sunrise']
            sunset = weather_data['sun_phase']['sunset']

            moonphase = weather_data['moon_phase']

            retval['sunrise'] = "%s:%s" % (sunrise['hour'], sunrise['minute'])
            retval['sunset'] = "%s:%s" % (sunset['hour'], sunset['minute'])
            retval['moonphase'] = moonphase['percentIlluminated']
            retval['current_time'] = "%s:%s" % (moonphase['current_time']['hour'], moonphase['current_time']['minute'])
            retval['moon_phase'] = weather_data['moon_phase']
        except:
            pass

        # let's make sure the tide data is set to two sig digits
        tide_info = weather_data['rawtide']['rawTideStats'][0]

        tide_info['minheight'] = "{0:.2f}".format(round(tide_info['minheight'], 2))
        tide_info['maxheight'] = "{0:.2f}".format(round(tide_info['maxheight'], 2))

        # now let's set the tide info
        retval['tide'] = tide_info

        return retval
