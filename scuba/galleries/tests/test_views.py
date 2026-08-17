from django.test import TestCase

from scuba.accounts.models import User
from scuba.galleries.models import Album


class TestAlbumViews(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')
        self.other_user = User.objects.get(email='test2@tester.com')
        self.album = Album.objects.create(user=self.user, title='My Trip')

    def test_showalbum_renders_for_owner(self):
        self.client.force_login(self.user)

        response = self.client.get(f'/gallery/albums/{self.album.pk_as_str}')

        self.assertEqual(response.status_code, 200)

    def test_showalbum_404s_for_non_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(f'/gallery/albums/{self.album.pk_as_str}')

        self.assertEqual(response.status_code, 404)

    def test_editalbum_404s_for_non_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(f'/gallery/albums/{self.album.pk_as_str}/edit/')

        self.assertEqual(response.status_code, 404)

    def test_showalbum_requires_login(self):
        response = self.client.get(f'/gallery/albums/{self.album.pk_as_str}')

        self.assertEqual(response.status_code, 302)
