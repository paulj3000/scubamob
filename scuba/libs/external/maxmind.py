import geoip2.database

import json
from pprint import pprint

from scuba.settings import MAXMIND_CITY_DB


class MaxMind:
    @staticmethod
    def get_city_data(ip):
        with geoip2.database.Reader(MAXMIND_CITY_DB) as reader:
            response = reader.city(ip)
            print(response.country.iso_code)
            print(response.city)
            print(response.location)

            return response.city, response.location

    @staticmethod
    def lookup(ip):

        # Attempt to decode the json data.  If we don't get valid data
        # send an alert to OPS
        try:
            ret = self.do_request(ip)
            decoded_json = json.loads(ret['response'])
        except:
            # JSON error, the return data was not JSON
            # for some reason, we cannot communicate w/ Quova.  Log the message, email OPS and return
            logmsg = ''
            #logmsg = "Error communicating w/ maxmind.  Response received:  %s\n" % ret['response']
            logmsg += "IP Address queried:  %s\n" % ip;

            #print(logmsg)

            return None     # something bad happened communicating w/ quova

        return decoded_json
