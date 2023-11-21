from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


@method_decorator([login_required], name='dispatch')
class IndexView(TemplateView):
    template_name = "accounts/collections/index.html"

    def get_context_datas(self, **kwargs):
        """ get_context_data

        override the get_context_data. add some extra data
        """
        context = super().get_context_data(**kwargs)
        return context
