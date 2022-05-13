from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

# define the user data for this account
from divesites.mongo import DiveSite as DiveSiteMongo
from home.forms import HomeLoginForm
from scuba.accounts.forms import AccountForm
from scuba.accounts.mongo import Account as AccountMongo
from utils.external.weather import Weather
from utils.maxmind import MaxMind


def index(us_request):
    if us_request.user.is_authenticated:
        return redirect('/home/')

    context     = {}

    # get maxmind data
    maxmind     = MaxMind()
    ip      = maxmind.get_client_ip(us_request)
    context['geoip']    = maxmind.get_maxmind_data(ip)

    # render the appropriate template
    return render(us_request, 'home/index.html', context)


@login_required
def home(us_request):
    user        = us_request.user
    user_id     = user.id

    #return redirect('account_settings')


    template    = 'home/home.html'

    divesite_mongo  = DiveSiteMongo()
    weather = Weather()

    # let's get the favorites for this particular user
    mongo_obj   = AccountMongo(user_id=user.id)
    user_favorites  = mongo_obj.get_favorites()
    context     = { 'divesites': [] }

    for fav in user_favorites:
        fav_data    = divesite_mongo.get_divesite_info(fav)
        weather_data    = weather.get_data_latlng(fav_data['latlng']['latitude'],\
                            fav_data['latlng']['longitude'])

        divesite_data   = divesite_mongo.get_divesite_info(fav)
        divesite_data['weather']    = weather_data

        context['divesites'].append(divesite_data)

    account = AccountMongo(user_id=user_id)

    # render the appropriate template
    return render(us_request, template, context)

