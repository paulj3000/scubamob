"""
scuba/content/urls_articles.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

These are the links for news section of the site
    * webhooks
"""
from django.urls import re_path

from scuba.content.views import articles as articles_views


urlpatterns = [
    re_path(r'^(?P<url>[0-9A-Za-z-]{1,255})$', articles_views.ArticleView.as_view()),
]
