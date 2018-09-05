from pprint import pprint
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.forms.models import model_to_dict

from account.models import UserFriendRequest, UserFriend
from account.mongo import Account as AccountMongo
from utils.jsonresponse import JSONResponse, api_response

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def setfavorite(us_request):
    user_id =   us_request.user.id
    
    divesiteid  = us_request.POST.get('divesite')
    favorite    = us_request.POST.get('favorite')

    if not divesiteid or not favorite:
        return HttpResponseBadRequest()

    account = AccountMongo(user_id=user_id)
    account.set_favorite(divesiteid, favorite)

    response    = {}
    return HttpResponse(response, content_type='application/json; charset=utf-8')

@login_required
@require_http_methods(["GET"])
def getfavorites(us_request):
    user_id =   us_request.user.id
    
    account = AccountMongo(user_id=user_id)
    account.get_favorites()

    response    = {}
    return HttpResponse(response, content_type='application/json; charset=utf-8')

@login_required
@require_http_methods(["POST"])
def deletefriend(us_request):
    user_id =   us_request.user.id
    
    account = AccountMongo(user_id=user_id)
    account.get_favorites()

    response    = {}
    return HttpResponse(response, content_type='application/json; charset=utf-8')
