"""
Tests for GetGalleryApi/GetAlbumsApi (CODE_REVIEW.md §3 item 15 --
self.request.id doesn't exist on HttpRequest) and GetPhotosApi
(item 16 -- missing return in get_queryset).
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.galleries.models import Album, Media


class TestGetGalleryAndAlbumsApi(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='gallery@nowhere.com', username='galleryuser', password='tester1234',
            first_name='Gallery', last_name='User')
        self.media = Media.objects.create(
            user=self.user, filename='photo.png', title='t', description='d',
            thumbnail='thumb.png')
        self.album = Album.objects.create(user=self.user, title='My Album')

    def test_gallery_returns_the_requested_users_media(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get(f'/api/profile/{self.user.pk_as_str}/media', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['media']), 1)

    def test_albums_returns_the_requested_users_albums(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get(f'/api/profile/{self.user.pk_as_str}/albums', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['albums']), 1)

    def test_gallery_of_a_user_who_blocked_you_is_forbidden(self):
        other = User.objects.get_or_create(
            email='blocker@nowhere.com', defaults={
                'username': 'blockeruser', 'first_name': 'Block', 'last_name': 'User'})[0]
        other.set_password('tester1234')
        other.save()
        other.block_buddy(self.user)

        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get(f'/api/profile/{other.pk_as_str}/media', format='json')

        self.assertEqual(response.status_code, 403)


class TestGetPhotosApi(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='photos@nowhere.com', username='photosuser', password='tester1234',
            first_name='Photos', last_name='User')
        Media.objects.create(
            user=self.user, filename='photo.png', title='t', description='d',
            thumbnail='thumb.png')

    def test_returns_the_callers_own_photos(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get(f'/api/profile/{self.user.pk_as_str}/photos', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
