"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from urllib.parse import urljoin

from django.test import TestCase

from scuba.home.models import Jumbotron
from scuba.settings import AWS_CLOUDFRONT


class TestHome(TestCase):
    fixtures = ["test_home.json"]

    def test_jumbotron_name(self):
        """
        Verify the name returned by the __str__ function matches
        the jumbotron name
        """
        for jumbotron in Jumbotron.objects.filter():
            self.assertEqual(str(jumbotron), jumbotron.name)

    def test_jumbotron_url(self):
        """
        Verify the url returned for the jumbotron matches what it
        is supposed to be
        """
        for jumbotron in Jumbotron.objects.filter():
            url = urljoin(AWS_CLOUDFRONT, jumbotron.filename)
            self.assertEqual(url, jumbotron.url)

    def test_get_active_jumbotron_single(self):
        """
        Get the active jumbotron - single
        """
        jumbotron = Jumbotron.objects.get(is_active=True)
        self.assertEqual(jumbotron.pk_as_str, Jumbotron.get_active_jumbotron().pk_as_str)

    def test_get_active_jumbotron_multiple(self):
        """
        Get the active jumbotron - multiple
        """
        Jumbotron.objects.update(is_active=True)
        jumbo = Jumbotron.objects.all().first()

        # if there are multiple, get the first one
        self.assertEqual(Jumbotron.get_active_jumbotron().pk_as_str, jumbo.pk_as_str)

    def test_no_active_jumbotron(self):
        """
        There are no active jumbotrons
        """
        Jumbotron.objects.update(is_active=False)

        # there should be no active jumbotrons
        self.assertIsNone(Jumbotron.get_active_jumbotron())

    def test_jumbotron_is_video(self):
        """
        Is the jumbotron a video
        """
        jumbotron = Jumbotron.objects.get(jumbotron_type=Jumbotron.JUMBOTRON_TYPE_VIDEO)
        self.assertTrue(jumbotron.is_video)
        self.assertFalse(jumbotron.is_image)

    def test_jumbotron_is_image(self):
        """
        Is the jumbotron an image
        """
        jumbotron = Jumbotron.objects.get(jumbotron_type=Jumbotron.JUMBOTRON_TYPE_IMAGE)
        self.assertFalse(jumbotron.is_video)
        self.assertTrue(jumbotron.is_image)
