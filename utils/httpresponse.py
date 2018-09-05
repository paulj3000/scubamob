import uuid, re, sys

from django.utils import simplejson
from django.http import HttpResponse
from django.conf import settings

class HttpResponseNotAuthorized(HttpResponse):
    def __init__(self):
        super(HttpResponseNotAuthorized, self).__init__()
        self.status_code = 401

def JSONResponse(data, httpclass=HttpResponse):
    return httpclass(json.dumps(data, cls=JSONEncoder), content_type='application/json; charset=utf-8')
