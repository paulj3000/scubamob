"""
Tests for NewsArticle: the get_published_articles() limit fix, the new
NewsArticleSerializer, and the newly-mounted news_index/news_article views.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.content.models import NewsArticle
from scuba.content.serializers import NewsArticleSerializer


class TestGetPublishedArticles(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')

    def test_returns_only_published_articles(self):
        published = NewsArticle.objects.create(
            title='Published', content='content', user=self.user, is_published=True)
        NewsArticle.objects.create(
            title='Draft', content='content', user=self.user, is_published=False)

        self.assertEqual(list(NewsArticle.get_published_articles()), [published])

    def test_respects_the_limit_argument(self):
        for i in range(3):
            NewsArticle.objects.create(
                title=f'Article {i}', content='content', user=self.user, is_published=True)

        self.assertEqual(len(NewsArticle.get_published_articles(limit=2)), 2)


class TestNewsArticleSerializer(TestCase):
    fixtures = ["test_users.json"]

    def test_serializes_title_url_excerpt_and_published_date(self):
        user = User.objects.get(email='foo@nowhere.com')
        article = NewsArticle.objects.create(
            title='A big dive news story', content='<p>' + ('word ' * 40) + '</p>',
            user=user, is_published=True)

        data = NewsArticleSerializer(article).data

        self.assertEqual(data['title'], 'A big dive news story')
        self.assertEqual(data['url'], reverse('news_article', kwargs={'url': article.url}))
        self.assertNotIn('<p>', data['excerpt'])
        self.assertTrue(data['excerpt'].endswith('…'))


class TestNewsViews(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')
        self.client = APIClient()

    def test_news_index_renders(self):
        NewsArticle.objects.create(
            title='Published', content='content', user=self.user, is_published=True)

        response = self.client.get(reverse('news_index'))
        self.assertEqual(response.status_code, 200)

    def test_published_article_is_reachable(self):
        article = NewsArticle.objects.create(
            title='Published', content='content', user=self.user, is_published=True)

        response = self.client.get(reverse('news_article', kwargs={'url': article.url}))
        self.assertEqual(response.status_code, 200)

    def test_unpublished_article_404s(self):
        article = NewsArticle.objects.create(
            title='Draft', content='content', user=self.user, is_published=False)

        response = self.client.get(reverse('news_article', kwargs={'url': article.url}))
        self.assertEqual(response.status_code, 404)
