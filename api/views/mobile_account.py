from pprint import pprint
import re, uuid, time, sys
from datetime import datetime, timedelta

from django.core.validators import validate_email
from django.forms import ValidationError
from django.http import HttpResponseNotFound, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.forms.models import model_to_dict

from scuba.accounts.models import User
from api.views.apiutils import trigger_response, process_request, UPDATER, REQUIRED
from utils.decorators import mobile_auth
from api.views.exceptions import *


CONFIG = 'CONFIG'
FIELD = 'ACCOUNT'

# creating our API Error Code object
API_Error_Codes = APIErrorCodes()

def account_firstname(user, value):
    value = value[0] if type(value) == list else value
    user.first_name = value
    return user

def account_lastname(user, value):
    value = value[0] if type(value) == list else value

    if not value:
        errors = API_Error_Codes.invalid_value('last_name')
        raise InvalidValueException(**errors)

    user.last_name = value
    return user

def account_email(user, value):
    value = value[0] if type(value) == list else value
    email_list = [ u.email for u in User.objects.filter(email=value).exclude(id=user.id)]
    if value in email_list:
        errors = API_Error_Codes.duplicate(value)
        raise InvalidValueException(**errors)

    user.email = value
    return user

def account_username(user, value):
    value = value[0] if type(value) == list else value
    user_list = [ u.username for u in User.objects.filter(username=value)]
    if value in user_list:
        errors = API_Error_Codes.duplicate(value)
        raise InvalidValueException(**errors)

    user.username = value
    return user

def account_password(user, value):
    user.set_password(value)
    return user

ACCOUNT_FIELDS = {
                      'username': { UPDATER : account_username },
                      'first_name': { UPDATER : account_firstname },
                      'last_name': { UPDATER : account_lastname },
                      'email': { UPDATER : account_email },
                      'password': { UPDATER : account_password }
                  }

REQUIRED_FIELDS = [i for i in ACCOUNT_FIELDS.keys()]
VALID_PARAMS = REQUIRED_FIELDS + [i for i in ACCOUNT_FIELDS.keys() if ACCOUNT_FIELDS[i].get(CONFIG)]


@csrf_exempt
@mobile_auth
def external(us_request, us_username=None):
    data = process_request(us_request)

    us_input_data = data['us_input_data']
    action = data['action']

    # which function shall we use?
    function = { 'PUT' : update, 'POST' : create, 'GET' : get }[action]

    # now call the function with all the appropriate data
    return trigger_response(function, us_request, us_input_data, us_username)

def update(us_request, us_input_data, us_username):
    print(f"us_username: {us_username}")
    # make sure we have a valid monitor id
    if not us_username:
        errors = API_Error_Codes.id_not_supplied(FIELD)
        raise InvalidIdException(**errors)

    user = User.objects.filter(username=us_username)

    try:
        user = user[0]
    except:
        errors = API_Error_Codes.id_not_supplied(FIELD)
        raise InvalidIdException(**errors)

    input_fields = set(us_input_data.keys())

    if not len(input_fields):
        # get our eror message.  The user did not supply any data in the post
        errors = API_Error_Codes.no_data_supplied_put()
        raise RequiredFieldMissingException(**errors)

    if set(input_fields).difference(VALID_PARAMS):
        invalid_fields = list((set(input_fields)).difference(VALID_PARAMS))

        errors = API_Error_Codes.invalid_fields(invalid_fields)
        raise InvalidFieldException(**errors)

    for field in us_input_data:
        if ACCOUNT_FIELDS[field].get(UPDATER) and field != 'username':
            user = ACCOUNT_FIELDS[field][UPDATER](user, us_input_data.get(field))

    user.save()

    response = api_response(data={'items': { 'updated' : user.id}})
    return JSONResponse(response)

def create(us_request, us_input_data, us_username):
    input_fields = set(us_input_data.keys())

    #account = get_from_model(us_username)

    if not len(input_fields):
        # get our eror message.  The user did not supply any data in the post
        errors = API_Error_Codes.no_data_supplied_post()
        raise RequiredFieldMissingException(**errors)

    if set(REQUIRED_FIELDS).difference(set(input_fields)):
        missing_fields = list(set(REQUIRED_FIELDS).difference(input_fields))

        # get our eror message
        errors = API_Error_Codes.missing_fields(missing_fields)
        raise RequiredFieldMissingException(**errors)

    if set(input_fields).difference(VALID_PARAMS):
        errors = API_Error_Codes.invalid_fields(list(set(input_fields).difference(VALID_PARAMS)))
        raise InvalidFieldException(**errors)

    user = User()
    for key in ACCOUNT_FIELDS:
        if ACCOUNT_FIELDS[key].get(UPDATER):
            user = ACCOUNT_FIELDS[key][UPDATER](user, us_input_data.get(key))

    user.save()
    User.objects.create(user=user)

    response = api_response(data={'items': { 'created' : '2013-09-01', 'id': user.id }})
    return JSONResponse(response)

def get(us_request, us_input_data, us_username):
    account = get_from_model(us_username)
    try:
        account_json = model_to_dict(account, fields=['username', 'email', 'last_name', 'first_name'])
        return JSONResponse(api_response(data={'items':[account_json] }))
    except:
        errors = API_Error_Codes.not_found(FIELD, us_username)
        raise InvalidIdException(**errors)


def get_from_model(us_username):
    if not us_username:
        errors = API_Error_Codes.id_not_supplied(FIELD)
        raise InvalidIdException(**errors)

    account = User.objects.filter(username=us_username)

    try:
        return account[0]
    except:
        errors = API_Error_Codes.not_found(FIELD, us_username)
        raise InvalidIdException(**errors)

def validate_datetime(date, offset, field):
    try:
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M')-timedelta(hours=offset)
        return date.strftime('%Y-%m-%dt%H:%M:00')

    except ValueError:
        try:
            date = datetime.strptime(date, '%Y-%m-%d')-timedelta(days=offset)
            return date.strftime('%Y-%m-%dt00:00:00')
        except:
            errors = API_Error_Codes.invalid_value(date, field)
            raise InvalidValueException(**errors)
