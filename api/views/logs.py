from datetime import datetime, timedelta
from pprint import pprint
from bson.objectid import ObjectId

from django.conf import settings
from django.http import QueryDict

from logbook.mongo import DiveLog
from api.views.apiutils import trigger_response, process_request
from utils.decorators import external_authentication


@external_authentication
def external(us_request, us_log_id=None):
    data = process_request(us_request)

    us_input_data   = data['us_input_data']
    action          = data['action']

    # which function shall we use?
    function = { 'PUT' : update, 'POST' : create, 'GET' : get, 'PATCH' : update }[action]

    # now call the function with all the appropriate data
    return trigger_response(function, us_request, us_input_data, us_log_id)

def get(us_request, us_input_data, us_log_id):
    extra_fields = us_request.GET.getlist('addField')
    sort_by = us_request.GET.get('sortBy')
    user    = us_request.META.get('user')

    offset  = 0
    total   = 0
    items   = []
    divelog    = DiveLog()

    if us_log_id:
        kwargs  = {'user_id': user.id , 'id': us_log_id }
        data = divelog.get_log( **kwargs)

        if not data or data['user_id'] != user.id:
            errors = API_Error_Codes.id_not_supplied('DIVELOG')
            raise InvalidIdException(**errors)

        data['id']  = str(data['_id'])
        del data['_id']
        if data.get('user_id'):
            del(data['user_id'])

        ### add this
        items.append(data)

    else:
        data = divelog.collection.find( {'user_id': user.id })

        for d in data:
            d['id']  = str(d['_id'])
            del d['_id']
            if d.get('user_id'):
                del(d['user_id'])
            items.append(d)

    response = api_response(data={'items':items, 'total': len(items), 'offset' : offset})
    return JSONResponse(response)

def update(us_request, us_input_data, us_log_id):
    divelog    = DiveLog()
    user    = us_request.META.get('user')

    kwargs  = {'user_id': user.id , 'id': us_log_id }
    dive_data = divelog.get_log( **kwargs)

    del(dive_data['_id'])

    if not dive_data:
        errors = API_Error_Codes.id_not_supplied('DIVELOG')
        raise InvalidIdException(**errors)

    for field in us_input_data:
        dive_data[field]   = us_input_data.get(field)

    divelog.collection.update({ '_id': ObjectId(us_log_id) }, { "$set": dive_data })
    response = api_response(data={'items':[{ 'modified': 'now' }]})
    return JSONResponse(response)

def create(us_request, us_input_data, us_divesite_id):
    user    = us_request.META.get('user')

    divelog    = DiveLog()
    log_create  = {'user_id': user.id }
    for field in us_input_data:
        log_create[field]   = us_input_data.get(field)

    data = str(divelog.collection.insert(log_create))

    #response = api_response(data={'items':items, 'total': len(items), 'offset' : offset})
    response = api_response()

    response = api_response(data={'items':[{ 'created': 'now', 'id': data }]})
    return JSONResponse(response)
