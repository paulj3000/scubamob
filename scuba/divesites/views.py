from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView

from scuba.divesites.forms import SiteForm



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
            'sites': Divesites.get_all_active_divesites(),
        })

        return context


def index(us_request):

    context = {}

    # render the appropriate template
    return render(us_request, 'divesites/index.html', context)


def site(us_request, url):

    context = {}

    # render the appropriate template
    return render(us_request, 'divesites/index.html', context)


@login_required
def newsite(us_request, siteid=None):
    user = us_request.user
    #if not user.account.can_add_divesites:
    #    raise Http404

    # render the appropriate template
    if us_request.method == 'POST':
        site_form = SiteForm(us_request.POST, user_id=us_request.user.id, site_id=siteid)
        if site_form.is_valid():
            messages.add_message(us_request, messages.INFO, 'Site successfully saved')
            site_form.save()
    elif siteid:
        site_form = SiteForm(user_id=us_request.user.id, site_id=siteid)
        divelog = site_form.findsite(siteid)
    else:
        site_form = SiteForm(user_id=us_request.user.id)

    context = {'site_form': site_form, 'title': 'Create a new Dive Site'}

    return render(us_request, 'divesites/edit.html', context)
