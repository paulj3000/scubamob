from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView

# define the user data for this account
from scuba.divesites.models import Divesite
from scuba.home.models import Jumbotron
from scuba.settings import SITE_NAME


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
        context.update({
            'jumbotron': Jumbotron.get_active_jumbotron(),
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    """ IndexView

    display the home page
    """
    template_name = 'home/home.html'
