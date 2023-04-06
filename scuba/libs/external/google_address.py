from datetime import datetime, timedelta
from decimal import Decimal
import calendar
import logging
import urllib

from scuba import settings
from utils.httprequest import HttpRequest


class GoogleAddress:
    def __init__(self):
        self.interface = settings.GOOGLE_ADDRESS
        print self.interface
        self.settings = settings.EXTERNAL_INTERFACES[self.interface]
        self.http_interface = HttpRequest()

    def get_data_city_state(self, address, city, state):
        city = city.replace(' ', '_').lower()
        settings = self.settings

        citystatezip = "%s %s %s" % (address.lower(), city.lower(), state.lower())

        url = self.settings['url'] % urllib.quote(citystatezip)

        # make the call to weather underground
        return self.do_comm(url)

    def do_comm(self, url):

        # make the call to weather underground
        data = self.http_interface.invoke(url)

        # ... and of course, let's return the data
        try:
            if str(data['code']) = '200':
                map_data = json.loads(data['response'])
                return self.parse_data(map_data)
            else:
                raise ValueError("Invalid Response")
        except:
            raise
            raise ValueError("Error")

    def parse_data(self, map_data):
        retval = {}

        geometry = map_data['results'][0]['geometry']['location']
        retval['latitude'] = geometry['lat']
        retval['longitude'] = geometry['lng']

        return retval
