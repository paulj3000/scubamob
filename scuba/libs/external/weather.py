import logging
import requests
import json

from scuba import settings
from scuba.libs.memcache import MemcacheClient


class Weather:
    def __init__(self):
        self.interface = settings.WEATHER_UNDERGROUND
        self.settings = settings.EXTERNAL_INTERFACES[self.interface]

    def get_data_city_state(self, city, state):
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

    def get_data_latlng(self, lat, lon):

        try:
            memcache = MemcacheClient('weather')
            memcache_key = "%s_%s" % (lat, lon)
            res = memcache.get(memcache_key)
            return simplejson.loads(res)
        except:
            pass

        url = self.settings['url_latlng'] % (self.settings['apikey'], lat, lon)
        res = self.do_comm(url)

        # do the communications
        try:
            memcache.set(memcache_key, simplejson.dumps(res), 3600)
        except:
            print("memcache not available")
            pass

        # let's return
        return res

    def do_comm(self, url):

        # make the call to weather underground
        data = self.http_interface.invoke(url)

        # ... and of course, let's return the data
        try:
            if str(data['code']) == '200':
                weather_data = simplejson.loads(data['response'])
                return self.parse_data(weather_data)
            else:
                raise ValueError("Invalid Response")
        except:
            raise ValueError("Error")

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
