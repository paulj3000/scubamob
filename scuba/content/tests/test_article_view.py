"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.urls import reverse
from django.test import TestCase

from scuba.content.models import Article
from scuba.accounts.models import User


class TestArticleView(TestCase):
    fixtures = ["test_users.json"]

    def test_article(self):
        """
        test article page
        """
        user = User.objects.filter().first()
        article = Article.objects.create(title='page title',
                                         content='page content',
                                         user=user)

        response = self.client.get(f'/articles/{article.url}')
        self.assertEqual(response.status_code, 404)

        article.publish()
        response = self.client.get(f'/articles/{article.url}')
        self.assertEqual(response.status_code, 200)
