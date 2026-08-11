"""
skm/content/urls_news.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

These are the links for news section of the site
    * webhooks
"""
from django.urls import path, re_path

from scuba.content import views as news_views

urlpatterns = [
    path('', news_views.NewsIndexView.as_view(), name="news_index"),
    re_path(r'^(?P<url>[\w-]{1,255})$',
            news_views.NewsArticleView.as_view(), name='news_article'),
]
