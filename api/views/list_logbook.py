import dateutil.parser
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from wm.account.models import *
from wm.api.views.utils import *
from wm.monitoring.models import *
from wm.utils.converter import *
from wm.utils.decorators import internal_api_authenticated, load_account, admin_read_permission, admin_load_account
from wm.utils.jsonresponse import JSONResponse
from wm.utils.log import Log, WARN
from wm.utils.external_connections import api_response

@internal_api_authenticated
def list(us_request):
    return list_internal(us_request)

@login_required
@load_account
def public_json(us_request):
    json_response = list_internal(us_request, accountId=us_request.account.squared_id)
    if us_request.GET.get('callback'):
       json_response.content = us_request.GET.get('callback') + "(" + json_response.content + ")"
    return json_response

def list_internal(us_request, accountId=None):
    remove_fields = us_request.GET.getlist('removeField') or []
    monitors, offset, total, more = select(us_request, accountId)
    items = Monitor.objects.to_json_internal(monitors, remove_fields)
    return JSONResponse(api_response(data={'items':items, 'total': total, 'offset' : offset, 'more' : more}))

## called from api.views.monitor.external
def list_external(us_request, accountId=None, external=True):
    extra_fields = us_request.GET.getlist('addField')
    sort_by = us_request.GET.get('sortBy')
    monitors, offset, total, more = select(us_request, accountId)
    items = Monitor.objects.to_json_external(monitors, extra_fields)
    if sort_by:
        reverse = sort_by.count('-') and sort_by.index('-') == 0
        sort_by = sort_by[1:] if sort_by[0] == '-' else sort_by
        sort_by.replace('-','')
        items.sort(key=lambda x: x.get(sort_by), reverse=reverse)
    response = api_response(data={'items':items, 'total': total, 'offset' : offset, 'more' : more}, external=external)
    APIResponse().remove_pagination(response)
    return JSONResponse(response)

@login_required
@load_account
def public_json_summary(us_request):
    json_response = summary(us_request, accountId=us_request.account.squared_id)
    if us_request.GET.get('callback'):
       json_response.content = us_request.GET.get('callback') + "(" + json_response.content + ")"
    return json_response

@login_required
@admin_read_permission
@admin_load_account
def admin_json_summary(us_request):
    default_fields = ['id','name','active','locations','type','frequency','steps','daily_units','daily_load_time','daily_uptime' ]
    fields = us_request.GET.getlist('field') or default_fields
    extra_fields = us_request.GET.getlist('addField')
    sort_by = us_request.GET.get('sortBy')
    monitors, offset, total, more = select(us_request)
    items = Monitor.objects.to_json_external(monitors, fields=fields)
    if sort_by:
        reverse = sort_by.count('-') and sort_by.index('-') == 0
        sort_by = sort_by[1:] if sort_by[0] == '-' else sort_by
        sort_by.replace('-','')
        items.sort(key=lambda x: x.get(sort_by), reverse=reverse)
    response = api_response(data={'items':items, 'total': total, 'offset' : offset, 'more' : more})
    json_response = JSONResponse(response)
    if us_request.GET.get('callback'):
       json_response.content = us_request.GET.get('callback') + "(" + json_response.content + ")"
    return json_response

def summary(us_request, accountId=None):
    monitors, offset, total, more = select(us_request, accountId)
    items = Monitor.objects.to_json_summary(monitors)
    response = api_response(data={'items':items, 'total': total, 'offset' : offset, 'more' : more})
    return JSONResponse(response)

## Determine which monitors we are going to include in the response
def select(us_request, accountId=None):
    monitors = Monitor.objects.filter(monitorofaccount__isOwner=True)

    ## filter if requested
    if hasattr(us_request, 'account'):
        account = us_request.account
        monitors = account.monitors

    if us_request.REQUEST.get('accountName'):
        us_account_names = us_request.REQUEST.getlist('accountName')
        monitors = monitors.filter(monitorofaccount__account__name__in=us_account_names)

    if accountId or us_request.REQUEST.get('accountId'):
        us_account_ids = [accountId] if accountId else us_request.REQUEST.getlist('accountId')
        monitors = monitors.filter(monitorofaccount__account__squared_id__in=us_account_ids)

    if us_request.REQUEST.get('testScriptId'):
        us_test_script_id = us_request.REQUEST['testScriptId']
        monitors = monitors.filter(test_script_version__test_script__script_id=us_test_script_id)

    if us_request.REQUEST.get('monitorId'):
        us_monitoring_id = us_request.REQUEST.get('monitorId')
        us_monitoring_id = guid_with_dash(us_monitoring_id)
        monitors = monitors.filter(id=us_monitoring_id)

    if us_request.REQUEST.get('laterThan'):
        try:
            later_than = dateutil.parser.parse(us_request.REQUEST['laterThan'][:19])
            monitors = monitors.filter(modified__gt=later_than)
        except Exception, ex:
            Log().object({'location':'api/views/list.select', 'error_code':'API008', 'description':'could not parse param: laterThan', 'exception':ex,'request':us_request})
            raise ex

    if us_request.REQUEST.get('include') != 'deleted':
        monitors = monitors.filter(deleted=False)

    if us_request.REQUEST.get('activeOnly'):
        monitors = monitors.filter(active=True)

    offset, total = 0, monitors.count()
    limit = total
    if us_request.REQUEST.get('limit') or us_request.REQUEST.get('offset'):
        try:
            offset = max(0,int(us_request.REQUEST.get('offset', 0)))
        except ValueError as ex:
            offset = 0
        try:
            limit = max(1,int(us_request.REQUEST.get('limit', total)))
        except ValueError as ex:
            limit = monitors.count()
        monitors = monitors[offset:offset+limit]

    return monitors,offset,total,(offset+limit) < total

"""
## Create a jsonifiable list of monitors and attributes
def wrap_up_as_response(monitors):
    ## create return object
    response = {
                 "result" : "OK",
                 "errors" : [],
                 "data" : {
                        "items" : monitors,
                        "offset" : 0,
                        "total"  : len(monitors)
                    }
               }

    ## return JSON object
    json_response = JSONResponse(response)
    return json_response
    """
