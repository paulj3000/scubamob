from django.shortcuts import redirect
from django.views.generic import TemplateView

from scuba.divesites.models import Divesite


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
            'divesites': Divesite.get_all_active_divesites(),
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
