from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView

# define the user data for this account
from scuba.divesites.models import Divesite
from scuba.divesites.mongo import DiveSite as DiveSiteMongo
from scuba.accounts.forms import AccountForm
from scuba.accounts.mongo import Account as AccountMongo
from scuba.home.models import Jumbotron


from utils.external.weather import Weather
from utils.maxmind import MaxMind


class IndexView(TemplateView):
    """ IndexView

    display the home page
    """
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        """ get_context_data

        add more parameters to the context data
        """
        context = super().get_context_data(**kwargs)
        maxmind = MaxMind()
        ip = maxmind.get_client_ip(self.request)
        context.update({
            'geoip':maxmind.get_maxmind_data(ip),
            'jumbotron': Jumbotron.get_active_jumbotron(),
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


@login_required
def home(us_request):
    user = us_request.user
    user_id = user.id

    template = 'home/home.html'

    divesite_mongo = DiveSiteMongo()
    weather = Weather()

    # let's get the favorites for this particular user
    print(user.pk_as_str)
    print(user.pk_as_str)
    print(user.pk_as_str)
    print(user.pk_as_str)
    print(user.pk_as_str)
    mongo_obj = AccountMongo(user_id=user.pk_as_str)
    user_favorites = mongo_obj.get_favorites()
    context = {'divesites': []}

    for fav in user_favorites:
        fav_data = divesite_mongo.get_divesite_info(fav)
        weather_data = weather.get_data_latlng(
            fav_data['latlng']['latitude'],
            fav_data['latlng']['longitude'])

        divesite_data = divesite_mongo.get_divesite_info(fav)
        divesite_data['weather'] = weather_data

        context['divesites'].append(divesite_data)

    account = AccountMongo(user_id=user_id)

    # render the appropriate template
    return render(us_request, template, context)
