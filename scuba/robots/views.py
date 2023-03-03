"""
skm/robots/views.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

The views for the robot stuff
"""
import re

from django.contrib.sitemaps import views as sitemap_views
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_page
from django.views.generic import ListView
from django.urls import NoReverseMatch, reverse

from scuba.robots import settings
from scuba.robots.models import Rule


class RuleList(ListView):
    """
    Returns a generated robots.txt file with correct mimetype (text/plain),
    status code (200 or 404), sitemap url (automatically).
    """
    model = Rule
    context_object_name = 'rules'
    cache_timeout = getattr(settings, 'CACHE_TIMEOUT')
    current_site = None

    def get_current_site(self, request):
        """ get_current_site

        get the current site from something (I'm tired of doing module strings)
        """
        if hasattr(settings, 'SITE_BY_REQUEST'):
            domain = re.sub(':\d+', '', request.get_host())
            return Site.objects.get(domain=domain)

        return Site.objects.get_current()

    def reverse_sitemap_url(self):
        try:
            if hasattr(settings, 'SITEMAP_VIEW_NAME'):
                return reverse(getattr(settings, 'SITEMAP_VIEW_NAME'))

            return reverse(sitemap_views.index)
        except NoReverseMatch:
            try:
                return reverse(sitemap_views.sitemap)
            except NoReverseMatch:
                pass

    def get_domain(self):
        scheme = 'https' if self.request.is_secure() else 'http'
        if not self.current_site.domain.startswith(('http', 'https')):
            return "%s://%s" % (scheme, self.current_site.domain)

        return self.current_site.domain

    def get_sitemap_urls(self):
        """ get_sitemap_urls

        get the sitemap urls
        """
        sitemap_urls = None

        if hasattr(settings, 'SITEMAP_URLS'):
            sitemap_urls = list(getattr(settings, 'SITEMAP_URLS'))

        if not sitemap_urls and hasattr(settings, 'USE_SITEMAP'):
            sitemap_url = self.reverse_sitemap_url()

            if sitemap_url is not None:
                if not sitemap_url.startswith(('http', 'https')):
                    sitemap_url = "%s%s" % (self.get_domain(), sitemap_url)
                if sitemap_url not in sitemap_urls:
                    sitemap_urls.append(sitemap_url)

        return sitemap_urls

    def get_queryset(self):
        """ get_queryset

        query the database and get the required data
        """
        return Rule.objects.filter(sites=self.current_site)

    def get_context_data(self, **kwargs):
        """ get_context_data

        override the get_context_data. add some extra data
        """
        context = super().get_context_data(**kwargs)
        context['sitemap_urls'] = self.get_sitemap_urls()
        if hasattr(settings, 'USE_HOST'):
            if hasattr(settings, 'USE_SCHEME_IN_HOST'):
                context['host'] = self.get_domain()
            else:
                context['host'] = self.current_site.domain
        else:
            context['host'] = None
        return context

    def render_to_response(self, context, **kwargs):
        return super().render_to_response(
            context, content_type='text/plain', **kwargs
        )

    def get_cache_timeout(self):
        """ get_cache_timeout

        return the cache timeout
        """
        return self.cache_timeout

    def dispatch(self, request, *args, **kwargs):
        """ dispatch

        override the dispatch for the class-based view
        """
        cache_timeout = self.get_cache_timeout()
        self.current_site = self.get_current_site(request)
        super_dispatch = super().dispatch
        if not cache_timeout:
            return super_dispatch(request, *args, **kwargs)
        key_prefix = self.current_site.domain
        cache_decorator = cache_page(cache_timeout, key_prefix=key_prefix)
        return cache_decorator(super_dispatch)(request, *args, **kwargs)


rules_list = RuleList.as_view()
