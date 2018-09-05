import re
import json
import datetime
import urllib2, pprint, urllib
from urllib2 import URLError, HTTPError

from django.http import QueryDict
from django.conf import settings

class HttpRequest:
    ''' 
    Here is the money for this module.  Basically it defines the http process
    and how we actually will run the different http requests
    ''' 
    def __init__(self):
        pass

    def invoke(self, request_url, data = {}, meta_data = {}):
        ## here is where the magic happens. The interface is passed
        ## in at object creation, which is all set from the settings.py file
        ## and (possibly) redefined in the localsettings.py file

        ## the user can send in a new endpoint, method timeout, and a bunch of
        ## crazy stuff if need be
        end_point   = meta_data.get('end_point','') 
        method      = meta_data.get('method','GET')
        timeout     = meta_data.get('timeout') if meta_data.get('timeout') else 30

        ## get the interface and modify it according to the caller
        request_url     = "%s%s" % (request_url, end_point) 

        ## headers
        headers = {'Content-type':'application/json','Accept':'application/json'}

        ## let's add some headers in case they are called for
        if meta_data.get('headers') and type(meta_data['headers']) == dict:
            headers = dict(headers.items() + meta_data['headers'].items())

        # merge the data into a single dictionary so we can submit the data appropriately
        retval      = {'headers': headers, 'method': method}
        try:
            if method == 'GET':
                if meta_data.get('GET'):
                    data            = dict(data.items() + meta_data['GET'].items())

                ## generate a request URL based on the GET string and data
                request_url     = self.generate_url(request_url, data)

                # store the URL
                retval['url']   = request_url
                retval['data']  = data

                ## set up the request
                url = urllib2.Request(request_url, headers=headers)
            else:
                get_params      = meta_data.get('GET', {})
                request_url     = self.generate_url(request_url, get_params)

                # store the URL
                retval['url']   = request_url

                # encode the data ONLY if we don't send the is_json parameter
                if not meta_data.get('post_as_json'):
                    data    =   urllib.urlencode(data)

                retval['data']  = data

                ## now set all of the data
                url = urllib2.Request(request_url, data=data, headers=headers)

            response = urllib2.urlopen(url, timeout=timeout)
            retval.update({ url: request_url, 'code': response.getcode(), 'response': response.read() })

        except URLError, ex:
            retval.update({ 'code': ex.code if hasattr(ex, 'code') else 0, url: request_url,
                        'response': ex.read() if hasattr(ex, 'read') else '' })
        except Exception, ex:
            retval.update({ 'code': 0, 'url': request_url, 'response': '' })

        ## return the data we need back
        return retval

    def generate_url(self, request_url, data):
        ''' with all the data brought in, be sure we generate a correct URL w/ 
        GET parameters
        '''
        if type(data)   == str:
            try:
                data    = simplejson.loads(data)
            except:
                data    = {}
        if data.items():
            request_url += '?' + "&".join([("%s=%s"%(i,j)) for i,j in data.items()])
        
        return request_url

class HttpTestStub:
    def __init__(self, type):
        self.type   = type

    results = None
    def invoke(self, meta_data, **options):
        return self.results
