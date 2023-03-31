import re

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from scuba.content.models import FAQSection, Page, NewsArticle


class FAQView(TemplateView):
    """ FAQView

    display the frequently asked quesitons page
    """
    template_name = 'content/faq.html'
    def get_context_data(self, **kwargs):
        """ get_context_data

        add more parameters to the context data
        """
        context = super(FAQView, self).get_context_data(**kwargs)
        context['faqs'] = FAQSection.objects.all().order_by('position')
        return context


class ContentView(TemplateView):
    """ FAQView

    display the frequently asked quesitons page
    """
    template_name = 'content/content.html'
    def get_context_data(self, **kwargs):
        """ get_context_data

        add more parameters to the context data
        """
        context = super().get_context_data(**kwargs)

        request = self.request

        url = re.sub(r'^\/', '', self.request.META.get('PATH_INFO'))

        context['page'] = get_object_or_404(Page, url=url)
        context['page_name'] = url

        if request.GET.get('m'):
            context['mobile'] = True

        return context


class PageTemplate(TemplateView):
    """ For page templates needed for Angular.js, handle the templates """

    path = None
    def get_context_data(self, **kwargs):
        """ get_context_data

        add some extra variables to the rendering context
        """
        context = super().get_context_data(**kwargs)
        template = kwargs.get('template')
        self.template_name = f"{self.path}/{template}.html"
        return context


class NewsIndexView(TemplateView):
    """ For page templates needed for Angular.js, handle the templates """
    template_name = "content/news/index.html"

    def get_context_data(self, **kwargs):
        """ get_context_data

        add some extra variables to the rendering context
        """
        context = super().get_context_data(**kwargs)
        context['articles'] = NewsArticle.get_published_articles()
        context['active'] = 'news'
        return context


class NewsArticleView(TemplateView):
    """ For page templates needed for Angular.js, handle the templates """
    template_name = "content/news/article.html"


    def get_context_data(self, **kwargs):
        """ get_context_data

        add some extra variables to the rendering context
        """
        print(kwargs['url'])
        context = super().get_context_data(**kwargs)
        context['article'] = get_object_or_404(NewsArticle, url=kwargs.get('url'))
        context['active'] = 'news'
        return context
