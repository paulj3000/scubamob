from pprint import pprint
import hashlib
import re

from django.conf import settings
from django.contrib.auth.models import User

from utils.httpresponse import HttpResponseNotAuthorized
from utils.memcache_client import MemcacheClient

def mobile_auth(function):

    def wrapper(us_request, *auth, **kwauth):

        # move this shit to a decorator
        if not mobile_login(us_request) and not settings.DEBUG:
            return HttpResponseNotAuthorized()

        # supposedly this works.  Let's return it
        return function(us_request, *auth, **kwauth)

    return wrapper


def mobile_login(us_request):
    # check for these headers.  Eventually these will be checked in
    # nginx.  For now, we will do it here
    mobile_app = us_request.META.get('HTTP_X_MOBILE_APP')
    mobile_device = us_request.META.get('HTTP_X_MOBILE_DEVICE')

    if mobile_app == settings.MOBILE_HEADER_APP and \
        settings.MOBILE_HEADER_DEVICES.get(mobile_device):

        # this is a successful login
        return True

    # chump!!!!
    return False


def user_authorized(function):

    def wrapper(us_request, *auth, **kwauth):

        if not mobile_login(us_request) and not settings.DEBUG:
            return HttpResponseNotAuthorized()

        # supposedly this works.  Let's return it
        return function(us_request, *auth, **kwauth)

    return wrapper

def external_authentication(function):

    def wrapper(us_request, *auth, **kwauth):
        # move this shit to a decorator
        authenticated = False

        username = us_request.META.get('HTTP_X_SM_USERNAME', None)
        if settings.DEBUG:
            # bypass the mobile authentication system
            authenticated = True

        elif mobile_login(us_request):
            authenticated = False
            auth_token = us_request.META.get('HTTP_X_AUTH_TOKEN', None)
            client_id = us_request.META.get('HTTP_X_CLIENT_ID', None)

            hashkey = hashlib.md5()
            hashkey.update(client_id)
            client_key = re.sub(r'\W', '', str(hashkey.digest()))

            # save the key in memcache....
            memcache = MemcacheClient('mobile')
            awsKey = memcache.get(client_key)

            if awsKey == us_request.META.get('HTTP_X_API_KEY', None):
                # reset the access time back to five mins
                memcache.set(client_key, awsKey, 300)
                authenticated = True

        if authenticated:
            # last check.
            try:
                # let's get the user from the database
                user = User.objects.get(username=username)
                us_request.META['user'] = user
            except:
                # we could not get the data from the database.  he is not authenticated
                authenticated = False

        if not authenticated:
            return HttpResponseNotAuthorized()

        # supposedly this works.  Let's return it
        return function(us_request, *auth, **kwauth)

    return wrapper
