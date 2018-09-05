from datetime import datetime, timedelta
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import QueryDict

from diveshops.mongo import DiveShop as DiveShop
from api.views.apiutils import trigger_response, process_request
from utils.jsonresponse import JSONResponse, api_response
from utils.decorators import external_authentication

@csrf_exempt
#@external_authentication
def external(us_request, us_diveshop_id=None):
    data = process_request(us_request)

    us_input_data   = data['us_input_data']
    action          = data['action']

    # which function shall we use?
    function = { 'PUT' : update, 'POST' : create, 'GET' : get, 'PATCH' : update }[action]

    # now call the function with all the appropriate data
    return trigger_response(function, us_request, us_input_data, us_diveshop_id)

def get(us_request, us_input_data, us_diveshop_id):
    extra_fields = us_request.GET.getlist('addField')
    sort_by = us_request.GET.get('sortBy')

    offset  = 0
    total   = 0
    items   = []
    diveshop    = DiveShop()

    if us_diveshop_id:
        kwargs  = {'id': us_diveshop_id }
        data = diveshop.get_log( **kwargs)

        if not data:
            errors = API_Error_Codes.id_not_supplied('DIVELOG')
            raise InvalidIdException(**errors)

        data['id']  = str(data['_id'])
        del data['_id']
        if data.get('user_id'):
            del(data['user_id'])
    
        ### add this
        items.append(data)

    else:
        data = diveshop.collection.find()

        for d in data:
            d['id']  = str(d['_id'])
            del d['_id']
            if d.get('user_id'):
                del(d['user_id'])
            items.append(d)

    response = api_response(data={'items':items, 'total': items, 'offset' : offset})
    return JSONResponse(response)

def update(us_request, us_input_data, us_diveshop_id):
    pass

def create(us_request, us_input_data, us_diveshop_id):
    pass

