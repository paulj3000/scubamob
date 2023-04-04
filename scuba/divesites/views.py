from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from scuba.divesites.models import Divesite


class IndexView(TemplateView):
    """ IndexView

    display the home page
    """
    template_name = 'divesites/index.html'

    def get_context_data(self, **kwargs):
        """ get_context_data

        add more parameters to the context data
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'sites': Divesite.get_all_active_divesites(),
        })

        return context


class SiteView(TemplateView):
    """ IndexView

    display the home page
    """
    template_name = 'divesites/site.html'

    def get_context_data(self, **kwargs):
        """ get_context_data

        add more parameters to the context data
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'site': Divesite.get_all_active_divesites(),
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        site = get_object_or_404(Divesite, url=kwargs.get('url'))

        # add the site to the user's recently viewed pages
        if request.user.is_authenticated:
            request.user.add_divesite_recently_viewed(site)

        kwargs['site'] = site

        return super().dispatch(request, *args, **kwargs)
