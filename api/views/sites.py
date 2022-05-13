from datetime import datetime, timedelta
from pprint import pprint

from django.conf import settings
from django.http import QueryDict

from divesites.mongo import DiveSite
from api.views.apiutils import trigger_response, process_request
from utils.decorators import external_authentication


@external_authentication
def external(us_request, us_divesite_id=None):
    data = process_request(us_request)

    us_input_data   = data['us_input_data']
    action          = data['action']

    # which function shall we use?
    function = { 'PUT' : update, 'POST' : create, 'GET' : get, 'PATCH' : update }[action]

    # now call the function with all the appropriate data
    return trigger_response(function, us_request, us_input_data, us_divesite_id)

def get(us_request, us_input_data, us_divesite_id):
    extra_fields = us_request.GET.getlist('addField')
    sort_by = us_request.GET.get('sortBy')

    offset  = 0
    total   = 0
    items   = []
    divesite    = DiveSite()

    if us_divesite_id:
        pass
    else:
        data = divesite.collection.find()

        for d in data:
            d['id']  = str(d['_id'])
            del d['_id']
            if d.get('user_id'):
                del(d['user_id'])
            items.append(d)

    response = api_response(data={'items':items, 'total': items, 'offset' : offset})
    return JSONResponse(response)

def update(us_request, us_input_data, us_divesite_id):
    pass

def create(us_request, us_input_data, us_divesite_id):
    pass

