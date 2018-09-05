import json
from datetime import datetime, timedelta
from decimal import Decimal
import calendar
import logging

from django.http import HttpResponse

from utils.converter import to_time_string, to_time_delta_string

#===============================================================================
# Globals 
#===============================================================================
logger = logging.getLogger('wm.json')

#===============================================================================
# Class Interface
#===============================================================================
class JSONEncoder(json.JSONEncoder):
    def default(self, value):
        if isinstance(value, datetime):
            return to_time_string(int(calendar.timegm(value.timetuple())), '%Y-%m-%dT%H:%M:%S.%f')
        if isinstance(value, Decimal):
            return float(value)
        return json.JSONEncoder.default(self, value)

def JSONResponse(data, httpclass=HttpResponse):
    return httpclass(json.dumps(data, cls=JSONEncoder), content_type='application/json; charset=utf-8')

#===============================================================================
# Utility functions 
#===============================================================================
def from_json(str, alt=None):
    """ This function will take JSON String and return the decoded python object 
    """
    if not str: return alt
    try:
        return json.loads(str)
    except Exception, e:
        logger.exception(e)
    return alt

def api_response(**args):
    response = { 'data' : {
                     'items' : [],
                     'offset' : 0,
                     'total' : 0,
                     'more' : False,
                 },
                 'errors' : [],
               }

    if args.get('data'):
        if args.get('data').get('items'):
            response['data']['items'] = args['data']['items']
            del args['data']['items']
        response['data'].update(args['data'])
        del args['data']
        response['data']['total'] = response['data']['total'] or len(response['data']['items'])
    response.update(args)

    if not response['errors']:
        del(response['errors'])

    ## row return our encoded items
    return response
