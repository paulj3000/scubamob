from datetime import datetime, timedelta
from pprint import pprint
import uuid
import time
import re
import hashlib
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods

from utils.memcache_client import MemcacheClient
from api.models import MobileAppCredentials
from utils.httpresponse import HttpResponseNotAuthorized
from utils.decorators import mobile_auth


@mobile_auth
@require_http_methods(["PUT"])
def initdevice(us_request, client_id):
    # convert the response to JSON

    retval = { 'data': { 'items': [] }}
    mobile_dev = MobileAppCredentials.objects.filter(client_id=client_id)
    # if we got this far, we have to assume we got a mobile device and the decorator took
    # care of it
    if mobile_dev:
        mobile_dev = mobile_dev[0]
        assert(mobile_dev.active)

    else:
        mobile_device = us_request.META.get('HTTP_X_MOBILE_DEVICE')

        # generate a secret token
        phone_id = "%s%i" % (mobile_device, int(time.mktime(time.gmtime())))

        secret = "%i.%s.%s" % (datetime.now().timetuple().tm_yday, \
                                mobile_device,
                                str(uuid.uuid1()).replace('-', ''))

        mobile_dev = MobileAppCredentials.objects.create(client_id=client_id, \
                                phone_id = phone_id,
                                secret_key = secret)
    try:
        assert(mobile_dev)
        mobile_dev = model_to_dict(mobile_dev, fields=['secret_key', 'client_id', 'phone_id'])
        retval['data']['items'].append(mobile_dev)
    except:
        # oops, something bad happend
        return HttpResponseNotAuthorized()

    # all is good, let's return this instance
    return JSONResponse(api_response(**retval))


@mobile_auth
@require_http_methods(["PUT"])
def mauth(us_request, client_id):
    # convert the response to JSON
    retval = { 'data': { 'items': [] }}

    us_input_data = {}
    # verify the header
    if us_request.META.get('CONTENT_TYPE', None) and \
        re.match('application/json', us_request.META.get('CONTENT_TYPE'), re.IGNORECASE) and \
            us_request.body:
                us_input_data = simplejson.loads(us_request.body)
    else:
        return HttpResponseNotAuthorized()

    try:
        phone_id = us_input_data['phone_id']
        mobile_dev = MobileAppCredentials.objects.filter(client_id=client_id, \
                                        phone_id=phone_id)

        mobile_dev = mobile_dev[0]
        assert(mobile_dev and mobile_dev.active)

        # save the key in memcache....
        memcache = MemcacheClient('mobile')
        temp_key = "%s%s" % (str(uuid.uuid1()).replace('-', ''), str(uuid.uuid1()).replace('-', ''))
        memcache.set(client_id, temp_key, 120)

        # and return it
        retval['data']['items'].append({ 'tempkey': temp_key })
    except:
        # oops, something bad happend
        return HttpResponseNotAuthorized()

    # all is good, let's return this instance
    return JSONResponse(api_response(**retval))


@mobile_auth
@require_http_methods(["PUT"])
def login(us_request, client_id):
    retval = []

    # convert the response to JSON
    retval = { 'data': { 'items': [] }}

    us_input_data = {}
    # verify the header
    if us_request.META.get('CONTENT_TYPE', None) and \
        re.match('application/json', us_request.META.get('CONTENT_TYPE'), re.IGNORECASE) and \
            us_request.body:
                us_input_data = simplejson.loads(us_request.body)
    else:
        raise
        return HttpResponseNotAuthorized()

    try:
        username = us_input_data.get('username')
        password = us_input_data.get('password')
        phone_id = us_input_data.get('phone_id')
        token = us_input_data.get('token')
        secret_key = us_input_data.get('secret_key')

        mobile_dev = MobileAppCredentials.objects.filter(client_id=client_id, \
                                        secret_key=secret_key,
                                        phone_id=phone_id)

        if mobile_dev:
            mobile_dev = mobile_dev[0]
            # a client id was passed in, is he authorized to use it?
            if mobile_dev.active != True:
                return HttpResponseNotAuthorized()

        memcache = MemcacheClient('mobile')
        temp_token = memcache.get(client_id)

        user = authenticate(username=username, password=password)

        # let's make sure he have a bunch of good stuff here.....
        assert(token and temp_token == token and user)

        # ...and finally, let's store it in memcache

        temp_key = "%s%s" % (str(uuid.uuid1()).replace('-', ''), str(uuid.uuid1()).replace('-', ''))
        hashkey = hashlib.md5()
        hashkey.update(client_id)
        client_key = re.sub(r'\W', '', str(hashkey.digest()))
        memcache.set(client_key, temp_key, 300)

        # and return it
        retval['data']['items'].append({ 'authkey': temp_key })
    except:
        return HttpResponseNotAuthorized()

    # all is good, let's return this instance
    return JSONResponse(api_response(**retval))


