# -----------------------------------------------------------------------------
# maxmind.py #
# (C) Copyright 2013, Digital Infinity Software. All rights reserved.
#
# Author: Pauljames Dimitriu
# -----------------------------------------------------------------------------
import re, time, base64, httplib
import json
from urlparse import urlparse
from pprint import pprint

from django.conf import settings

from utils.httprequest import HttpRequest

class MaxMind():
    def __init__(self, *args, **kwargs):
        pass

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


    def get_maxmind_data(self,ip):

        # Attempt to decode the json data.  If we don't get valid data
        # send an alert to OPS
        try:
            ret = self.do_request(ip)
            decoded_json = json.loads(ret['response'])
        except:
            # JSON error, the return data was not JSON
            # for some reason, we cannot communicate w/ Quova.  Log the message, email OPS and return
            logmsg      = "Error communicating w/ maxmind.  Response received:  %s\n" % ret['response']
            logmsg     += "IP Address queried:  %s\n" % ip;

            print logmsg

            return None     # something bad happened communicating w/ quova

        return decoded_json

    def do_request(self, ip):
        username = 'Basic ' + base64.b64encode('%s:%s' % (settings.MAXMIND_USER, settings.MAXMIND_LICENSE)) + '==='
        url =  settings.MAXMIND_URL % ip
        http_obj    = HttpRequest()
        return http_obj.invoke(url, {}, { 'headers': { 'Authorization': username }})
