from django.shortcuts import redirect
from django.views.generic import TemplateView

# define the user data for this account


class IndexView(TemplateView):
    """ IndexView

    display the home page
    """
    template_name = 'home/index.html'


class HomeView(TemplateView):
    """ IndexView

    display the home page
    """
    template_name = 'home/home.html'
