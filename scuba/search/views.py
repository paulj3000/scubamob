from django.views.generic import TemplateView

from scuba.search.models import SearchLocation
from scuba.settings import SITE_NAME


class SearchView(TemplateView):
    """ SearchView

    display the search page
    """
    template_name = 'search/search.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            get = self.request.GET

            print(" INEHERE >>>> ")

            if get.get('location'):
                print(" INEHERE 22 >>>> ")
                p, created = SearchLocation.objects.get_or_create(
                    user=request.user,
                    location=get['location'])

                print(p)
                if not created:
                    p.save()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ get_context_data

        add more parameters to the context data
        """
        get = self.request.GET
        context = super().get_context_data(**kwargs)
        location = get.get('location', 'San Diego')
        search = get.get('search', '')

        context.update({
            'title': f"Top {search} in {location} - {SITE_NAME}"
        })

        return context
