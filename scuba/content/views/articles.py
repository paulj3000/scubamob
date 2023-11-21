import re

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from scuba.content.models import FAQSection, Page, Article


class ArticleView(TemplateView):
    """ ArticleView

    display the frequently asked quesitons page
    """
    template_name = 'content/article.html'

    def get_context_data(self, **kwargs):
        """ get_context_data

        add more parameters to the context data
        """
        context = super().get_context_data(**kwargs)

        request = self.request
        url = request.META.get('PATH_INFO').rsplit('/', 1)[-1]
        context['page'] = get_object_or_404(Article, url=url, is_published=True)
        context['page_name'] = url

        if request.GET.get('m'):
            context['mobile'] = True

        return context
