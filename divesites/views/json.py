from pprint import pprint
from bson import BSON
from bson import json_util
import json

# Create your views here.
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

# define the user data for this account
from scuba.accounts.mongo import Account as AccountMongo
#from home.forms import AccountForm, UserCreateForm
from utils.external.weather import Weather

from divesites.mongo import DiveSite


def getdivesites(us_request):
    retval = []

    diveSiteMongo = DiveSite()

    for site in diveSiteMongo.get_all_sites():
        site['id'] = str(site['_id'])
        del site['_id']
        retval.append(site)

    # convert the response to JSON
    return JsonResponse({'sites': retval})

@login_required
@require_http_methods(["GET"])
def getdivesiteinfo(us_request, siteid):
    retval = {}

    diveSiteMongo = DiveSite()
    divesiteinfo = diveSiteMongo.get_divesite_info(siteid)
    divesiteinfo['id'] = str(divesiteinfo['_id'])
    del divesiteinfo['_id']

    retval['divesiteinfo'] = divesiteinfo
    retval['id'] = divesiteinfo['id']

    if not divesiteinfo:
        raise Http404

    weather = Weather()
    weather_data = None
    try:
        address = divesiteinfo['address']
        weather_data = weather.get_data_city_state(address['city'],
                            address['state'])

        retval['weather'] = weather_data['current_observation']

        try:
            sunrise = weather_data['sun_phase']['sunrise']
            sunset = weather_data['sun_phase']['sunset']

            moonphase = weather_data['moon_phase']

            retval['sunrise'] = "%s:%s" % (sunrise['hour'], sunrise['minute'])
            retval['sunset'] = "%s:%s" % (sunset['hour'], sunset['minute'])
            retval['moonphase'] = moonphase['percentIlluminated']
            retval['current_time'] = "%s:%s" % (moonphase['current_time']['hour'], moonphase['current_time']['minute'])
            retval['moon_phase'] = weather_data['moon_phase']
        except:
            pass


        # let's make sure the tide data is set to two sig digits
        tide_info = weather_data['rawtide']['rawTideStats'][0]

        tide_info['minheight'] = "{0:.2f}".format(round(tide_info['minheight'], 2))
        tide_info['maxheight'] = "{0:.2f}".format(round(tide_info['maxheight'], 2))

        # now let's set the tide info
        retval['tide'] = tide_info

        user_id = us_request.user.id
        account = AccountMongo(user_id=user_id)
        retval['favorite'] = account.is_favorite(siteid)

    except:
        print("exception thrown.....")
        pass

    # convert the response to JSON
    return JsonResponse(api_response(data={'items': [retval]}))
