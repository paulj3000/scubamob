from pprint import pprint
import uuid, re, sys
import json
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.conf import settings
from django.http import HttpResponseNotFound, QueryDict

from api.views.exceptions import *

UPDATER = 'UPDATER'
REQUIRED = 'REQUIRED'
CONFIF = 'CONFIG'

def trigger_response(function, us_request, us_input_data, us_id):
    try:
        response = function(us_request, us_input_data, us_id)
    except InvalidIdException as ex:
        return JSONResponse(ex.json, httpclass=HttpResponseNotFound)
    except CannotCompleteAction as ex:
        return JSONResponse(ex.json, httpclass=HttpResponseBadRequest)
    except InvalidFieldException as ex:
        return JSONResponse(ex.json, httpclass=HttpResponseBadRequest)
    except InvalidValueException as ex:
        return JSONResponse(ex.json, httpclass=HttpResponseBadRequest)
    except RequiredFieldMissingException as ex:
        return JSONResponse(ex.json, httpclass=HttpResponseBadRequest)
    except CatastrophicException as ex:
        return JSONResponse(ex.json, httpclass=HttpResponseServerError)
    except:
        return JSONResponse({}, httpclass=HttpResponseServerError)

    return response or JSONResponse()

def process_request(us_request):
    # ..and make sure we have a valid request method.  Since we're doing
    # standard CRUD methodology, we need to make sure we have at least the
    # 'GET' verb
    request_method = us_request.META.get('REQUEST_METHOD', 'GET')
    us_input_data = {}        # declare a variable

    if request_method == 'POST' or request_method == 'PUT':
        # verify the header
        if us_request.META.get('CONTENT_TYPE', None) and \
            re.match('application/json', us_request.META.get('CONTENT_TYPE'), re.IGNORECASE) and \
            us_request.body:

            try:
                us_input_data = QueryDict('', mutable=True)
                us_input_data.update(simplejson.loads(us_request.body))
            except:
                us_input_data = QueryDict('', mutable=True)

        elif us_request.body:
            # kind of a crappy way to do this, but parse out the raw data and
            # turn it into a dict
            us_input_data = QueryDict(us_request.body, mutable=True)
    else:
        us_input_data = QueryDict(us_request.META.get('QUERY_STRING'), mutable=True)


    action = us_input_data.get("_method") if us_input_data.get("_method") else us_request.META.get('REQUEST_METHOD')
    action = action.upper()

    return { 'action': action, 'us_input_data': us_input_data, \
            'request_method': request_method }


class HttpResponseNotAuthorized(HttpResponse):
    def __init__(self):
        super(HttpResponseNotAuthorized, self).__init__()
        self.status_code = 401

def invalid(us_request, invalid):
    return JSONResponse({ "errors": { "message": "Resource %s not available" % invalid, "code": "MON_0000"  }}, httpclass=HttpResponseNotFound)


#===============================================================================
# Define some return stuff
#===============================================================================
class APIResponse():
    def paginate(self, data, offset):
        count = data.get('count', 0)
        total = data.get('total', '0')
        data['offset'] = offset

        if count + offset >= total:
            data['more'] = False
        else:
            data['more'] = True

    def remove_pagination(self, data):
        items = data['data']

        if 'more' in items:
            del(items['more'])

        if 'total' in items:
            del(items['total'])

        if 'offset' in items:
            del(items['offset'])

    def validate_pagination(self, data):
        items = data['data']

        if items.get('total', 0) < settings.QUERY_LIMIT:
            self.remove_pagination(data)

#===============================================================================
# Define error codes
#===============================================================================
class APIErrorCodes():
    def __init__(self):
        self.code = 'code'
        self.message = 'message'
        self.field = 'field'

    def not_found(self, field, monitor_id):
        message = "%s with Id '%s' not found."%(field, monitor_id)
        return { self.code:  'MON_0001', self.message: message   }

    def duplicate(self, name):
        return { self.code:  'MON_0002', self.message: "Duplicate name '%s' found."%name  }

    def missing_fields(self, missing_fields, valid_fields = [], optional_fields = []):
        if len(missing_fields) == 1:
            message = "%s is a required field." % missing_fields[0]
        else:
            message = "%s are required fields." % ', '.join(missing_fields)

        # return our message
        retval = { self.code:  'MON_0003', self.message: message }
        if len(valid_fields):
            retval.update({ 'validFields': valid_fields})
        if len(optional_fields):
            retval.update({ 'optionalFields': optional_fields})

        return retval

    def invalid_value(self, value, field, valid_values = []):
        message = "'%s' is an invalid value."% str(value)
        retval = { 'validValues': valid_values } if len(valid_values) else {}
        retval.update({ self.code: 'MON_0004', self.message: message, self.field: field })
        return retval

    def invalid_field_type(self, value, field, expected):
        message = "'%s' is an invalid value type.  Type '%s' expected" % (str(value), str(expected))
        return { self.code:  'MON_0005', self.message: message, 'field': field     }

    def invalid_fields(self, invalid_fields):
        if len(invalid_fields) == 1:
            message = "%s is an invalid field" % invalid_fields[0]
        else:
            message = "%s are invalid fields" % ', '.join(invalid_fields)

        # return our message
        retval = { self.code:  'MON_0006', 'message': message }
        return retval

    def id_not_supplied(self, field):
        message = "Valid %s id not supplied" % field
        return { self.code:  'MON_0007', self.message: message   }

    def no_data_supplied_post(self):
        message = "Empty body received in POST"
        return { self.code:  'MON_0008', self.message: message   }

    def no_data_supplied_put(self):
        message = "Empty body received in PUT"
        return { self.code:  'MON_0009', self.message: message   }

    def cannot_complete_request(self, field, message):
        return { self.code:  'MON_0010', self.message: message   }


    def system_error(self):
        return { self.code:  'MON_9999', self.message: 'An internal error has occured'     }
