import re
import time
import hashlib
from datetime import datetime
from functools import wraps
from django.http import HttpResponseForbidden
from django.conf import settings

from rs.settings import MOBILE_PASSWORD
from account.models import Account

from utils.httpresponse import JSONResponse, api_response
        
FIVE_MINS_PER_SECS  = 300 

def api_authentication(function):
    """
    Calls function if request is authenticated, else returns http 403
    """
   
    @wraps(function)
    def decorator(request, *args, **kwargs):
        # we have a username brought in to us.  Let's make sure
        # he's in the system

        #### let's make sure we have the correct header and the header is within 
        #### the appropriate range

        #### get the current time, get the upper an dlower bounds
        timespan            = int(time.time())
        timespan_lower      = timespan - FIVE_MINS_PER_SECS
        timespan_upper      = timespan + FIVE_MINS_PER_SECS

        apikey              = request.GET.get('apikey')
        signature           = request.GET.get('sig')
        timespan           = request.GET.get('timespan', 0)

        try:
            account = Account.objects.get(apikey=apikey)
        except:
            return generate_invalid_signature()

        ### get the secret portion of the API
        secret              = account.secret

        #### in order for this to work, we have to validate the 
        #### signature that was sent over.  THis means rebuild the signature
        #### with every time permutation until we hit paydirt
        for t in range(timespan_lower, timespan_upper):
            sig = hashlib.md5("%s%s%d" % (apikey, secret, t))

            if sig.hexdigest() == signature:
                #### the data matches.  run the function and return
                request.META['user']    = account.user 
                return function(request, *args, **kwargs)

        return generate_invalid_signature()

    def generate_invalid_signature():
        error   = { 'errors': [{ 'message': 'Invalid Signature', 'code': 'API_0000' }]}
        return JSONResponse(api_response(**error), HttpResponseForbidden)

    return decorator


def mobile_api_authentication(function):

    @wraps(function)
    def decorator(request, *args, **kwargs):
        ### let's define a constant 

        #### let's make sure we have the correct header and the header is within 
        #### the appropriate range
        rs_mobile_password = request.META.get('HTTP_RS_MOBILE', None)

        try:
            rs_mobile_timespan = int(request.META.get('HTTP_RS_TIMESPAN', 0))
        except ValueError:
            rs_mobile_timespan = 0

        #### get the current time, get the upper an dlower bounds
        timespan            = int(time.time())
        timespan_lower      = timespan - FIVE_MINS_PER_SECS
        timespan_upper      = timespan + FIVE_MINS_PER_SECS

        #### validate the request
        if str(rs_mobile_password) != str(MOBILE_PASSWORD):
            return JSONResponse({'bad': MOBILE_PASSWORD,'test2': rs_mobile_password }, HttpResponseForbidden)

        if rs_mobile_timespan < timespan_lower or rs_mobile_timespan > timespan_upper:
            return JSONResponse({ 'time': timespan, 'request': rs_mobile_timespan }, HttpResponseForbidden)

        return function(request, *args, **kwargs)
    
    return decorator
