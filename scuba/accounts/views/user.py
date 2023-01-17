import time
from pprint import pprint
import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, QueryDict
from django.contrib.auth.models import User
from rs.settings import MOBILE_PASSWORD

from api.views.core import *
from api.libs.decorators import api_authentication

api_error_codes = APIErrorCodes()

def user_first_name(user, value):
    value = value[0] if type(value) == list else value
    user.first_name = value
    return user

def user_last_name(user, value):
    value = value[0] if type(value) == list else value
    user.last_name = value
    return user

def user_email(user, value):
    value = value[0] if type(value) == list else value

    if User.objects.filter(email=value).exclude(id=user.id):
        errors = api_error_codes.duplicate('email', value)
        raise InvalidValueException(**errors)
    try:
        user.email  = value
    except:
        errors = api_error_codes.invalid_value(value, 'email')
        raise InvalidValueException(**errors)
    return user

def user_password(user, value):
    value = value[0] if type(value) == list else value

    if len(value) < 8:
        errors = api_error_codes.invalid_value(value, 'password')
        raise InvalidValueException(**errors)

    user.set_password(value)
    return user

USER_FIELDS =  {
                      'first_name':      { REQUIRED : True, UPDATER : user_first_name },
                      'last_name':       { REQUIRED : True, UPDATER : user_last_name },
                      'email':           { REQUIRED : True, UPDATER : user_email },
                      'password':        { REQUIRED : True, UPDATER : user_password },
                  }

REQUIRED_FIELDS = [ i for i in USER_FIELDS.keys() if USER_FIELDS[i].get(REQUIRED) ]
VALID_PARAMS  = REQUIRED_FIELDS + [ i for i in USER_FIELDS.keys() if USER_FIELDS[i].get(CONFIG) ]

# instantiate our invalid field types
class InvalidUserFieldException(InvalidFieldException):
    DESCRIPTION = "Invalid field name. Valid field names are %s: "%(" ".join(VALID_FIELDS))

# Create your views here.
@csrf_exempt
@api_authentication
def home(request, username=None):
    data = process_request(request)

    input_data = data['input_data']
    action = data['action']

    # now call the function with all the appropriate data
    try:
        function = { 'PUT' : update, 'GET' : get, 'PATCH' : update }[action]
        return trigger_response(function, request, input_data, username)
    except KeyError:
        errors = api_error_codes.invalid_method(action)
        ex =  InvalidMethodException(**errors)
        return JSONResponse(ex.json, httpclass=HttpResponseBadRequest)

def get(request, input_data, username):

    ### a simple function for returning the user information
    if username:
        try:
            user    = User.objects.get(username=username)
            account = user.account.first()
        except:
            errors  = api_error_codes.invalid_id(username)
            raise InvalidIdException(**errors)
        if account.is_private:
            errors  = api_error_codes.forbidden_request_exception()
            raise ForbiddenRequestException(**errors)
    else:
        user    = request.META.get('user')

    ### prepare our return value
    retval  = { 'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'username': user.username,
              }

    return JSONResponse(api_response(data={'items':[retval]}))

def update(request, input_data, username):
    if username:
        #### NO FRIGGEN WAY
        pass

    ### This function will update the user information
    user    = request.META.get('user')

    input_fields = set(input_data.keys())

    if not len(input_fields):
        # get our eror message.  The user did not supply any data in the post
        errors  = api_error_codes.no_data_supplied_put()
        raise RequiredFieldMissingException(**errors)

    if set(input_fields).difference(VALID_PARAMS):
        invalid_fields = list((set(input_fields)).difference(VALID_PARAMS))

        errors = api_error_codes.invalid_fields(invalid_fields)
        raise InvalidUserFieldException(**errors)

    for field in input_data:
        if USER_FIELDS[field].get(UPDATER):
            user = USER_FIELDS[field][UPDATER](user, input_data.get(field))

    # save the user
    user.save()

    response = api_response(data={'items': { 'updated' : user.id}})
    return JSONResponse(response)


@csrf_exempt
@api_authentication
def subscribe(request, calendarid):
    # get our data
    data = process_request(request)

    # now call the function with all the appropriate data
    return trigger_response(do_subscribe, request, data['input_data'], calendarid)

def do_subscribe(request, input_data, calendarid):
    user    = request.META.get('user')
    try:
        calendar = Calendar.objects.get(id=calendarid)
    except:
        errors = api_error_codes.invalid_id(calendarid)
        raise InvalidIdException(**errors)

    #### ok, supposedly we have a calendar.  Let's make sure we ahve
    #### permissions to do this

@csrf_exempt
@api_authentication
def friends(request, username=None):
    # get our data
    data = process_request(request)

    # now call the function with all the appropriate data
    return trigger_response(do_subscribe, request, data['input_data'], username)

def do_friends(request, input_data, username):
    user    = request.META.get('user')
    '''
    try:
        calendar = Calendar.objects.get(id=calendarid)
    except:
        errors = api_error_codes.invalid_id(calendarid)
        raise InvalidIdException(**errors)
    '''

    #### ok, supposedly we have a calendar.  Let's make sure we ahve
    #### permissions to do this

@csrf_exempt
@mobile_api_authentication
def create(request):

    data = process_request(request)
    input_data  = data['input_data']

    #### get the username......
    username = input_data.pop('username')
    username = username[0] if type(username) == list else username

    input_fields = set(input_data.keys())


    ### first, look for a user with the username.....

    if not len(input_fields):
        # get our eror message.  The user did not supply any data in the post
        errors  = api_error_codes.no_data_supplied_post()
        raise RequiredFieldMissingException(**errors)

    if set(REQUIRED_FIELDS).difference(set(input_fields)) or not username:
        missing_fields = list(set(REQUIRED_FIELDS).difference(input_fields))

        if not username:
            missing_fields.append('username')

        # get our eror message
        errors  = api_error_codes.missing_fields(missing_fields)
        raise RequiredFieldMissingException(**errors)

    if set(input_fields).difference(VALID_PARAMS):
        errors  = api_error_codes.invalid_fields(list(set(input_fields).difference(VALID_PARAMS)))
        raise RequiredFieldMissingException(**errors)


    #### before we start the process, make sure the requested username is not taken
    if User.objects.filter(username=username):
        errors  = api_error_codes.duplicate('username', username)
        ex =  RequiredFieldMissingException(**errors)
        return JSONResponse(ex.json, httpclass=HttpResponseForbidden)

    #### ....or what if the email address is taken
    if User.objects.filter(email=input_data['email']):
        errors  = api_error_codes.duplicate('email', input_data['email'])
        ex =  RequiredFieldMissingException(**errors)
        return JSONResponse(ex.json, httpclass=HttpResponseForbidden)

    user = User()

    ### set this username
    user.username   = username

    for key in USER_FIELDS:
        if USER_FIELDS[key].get(UPDATER):
            calendar = USER_FIELDS[key][UPDATER](user, input_data.get(key))

    ## save the calendar
    user.save()
    response = api_response(data={'items': { 'id': user.id }})
    return JSONResponse(response)
