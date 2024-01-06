import geoip2.database

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
