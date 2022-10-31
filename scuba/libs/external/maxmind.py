import json
from pprint import pprint

from scuba import settings


class MaxMind():
    @staticmethod
    def get_client_ip(request):
        if settings.DEBUG:
            return settings.DEBUG_IP

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

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
