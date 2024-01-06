"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.content.models import Article


class TestAccountsAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_get_article_title(self):
        """
        test an article's title
        """
        user = User.objects.get(email='foo@nowhere.com')
        article = Article.objects.create(title='unit test',
                                         content='some content',
                                         user=user)
        article.publish()
        self.assertEqual(article.title, article.__str__())

    def test_get_an_existing_article(self):
        """
        test an article that exists
        """
        user = User.objects.get(email='foo@nowhere.com')
        article = Article.objects.create(title='unit test',
                                         content='some content',
                                         user=user)
        article.publish()

        url = f'/articles/{article.url}'

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_an_existing_article_as_mobile(self):
        """
        test an article that may not exist
        """
        user = User.objects.get(email='foo@nowhere.com')
        article = Article.objects.create(title='unit test',
                                         content='some content',
                                         user=user)
        article.publish()

        url = f'/articles/{article.url}?m=1'

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_a_non_existing_article(self):
        """
        test an article that may not exist
        """
        url = '/articles/this-is-a-nonexistant-article'

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
