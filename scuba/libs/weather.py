import requests
from django.conf import settings

from scuba.libs.exceptions import InvalidWeatherDataException

# weatherapi.com settings
WEATHER_API = {
    'current': 'http://api.weatherapi.com/v1/current.json',
    'forecast': 'http://api.weatherapi.com/v1/forecast.json',
}


class Weather:

    @staticmethod
    def get_api_key():
        return settings.WEATHER_API_KEY

    @staticmethod
    def gen_param_lat_lon(lat, lng):
        return f'q={lat},{lng}'

    @staticmethod
    def gen_param_postal(lat, lng):
        return f'q={lat},{lng}'

    '''
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
    '''

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
