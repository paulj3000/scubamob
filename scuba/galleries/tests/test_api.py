from io import BytesIO
from unittest import mock

from PIL import Image as PILImage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.galleries.models import Album, AlbumImage, DailyImage


def _make_image_file(name='test.png', content_type='image/png'):
    buf = BytesIO()
    PILImage.new('RGB', (20, 20)).save(buf, format='PNG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type=content_type)


class TestGalleryApi(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')
        self.other_user = User.objects.get(email='test2@tester.com')
        self.client_api = APIClient()
        self.client_api.force_login(self.user)

    def test_create_album(self):
        response = self.client_api.post(
            '/api/galleries/createalbum/', {'title': 'My Trip', 'description': 'fun'})

        self.assertEqual(response.status_code, 200)
        album = Album.objects.get(user=self.user)
        self.assertEqual(album.title, 'My Trip')
        self.assertIn(album.pk_as_str, response.json()['url'])

    def test_list_albums(self):
        Album.objects.create(user=self.user, title='B Trip')
        Album.objects.create(user=self.user, title='A Trip')
        Album.objects.create(user=self.other_user, title='Not Mine')

        response = self.client_api.get('/api/galleries/albums')

        self.assertEqual(response.status_code, 200)
        titles = [a['title'] for a in response.json()['albums']]
        self.assertEqual(titles, ['A Trip', 'B Trip'])

    def test_delete_album_removes_it(self):
        album = Album.objects.create(user=self.user, title='Trip')

        response = self.client_api.delete(f'/api/galleries/deletealbum/{album.pk_as_str}')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Album.objects.filter(id=album.id).exists())

    def test_delete_someone_elses_album_is_rejected(self):
        album = Album.objects.create(user=self.other_user, title='Not yours')

        response = self.client_api.delete(f'/api/galleries/deletealbum/{album.pk_as_str}')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Album.objects.filter(id=album.id).exists())

    def test_get_album_images(self):
        album = Album.objects.create(user=self.user, title='Trip')
        AlbumImage.objects.create(album=album, image='full.png', thumbnail='thumb.png')

        response = self.client_api.get(f'/api/galleries/getalbumimages/{album.pk_as_str}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['images']), 1)

    def test_get_album_images_scoped_to_owner(self):
        album = Album.objects.create(user=self.other_user, title='Not yours')
        AlbumImage.objects.create(album=album, image='full.png', thumbnail='thumb.png')

        response = self.client_api.get(f'/api/galleries/getalbumimages/{album.pk_as_str}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['images'], [])

    def test_daily_pic_with_no_image_returns_null(self):
        response = self.client_api.get('/api/galleries/daily')

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['image'])

    def test_daily_pic_with_image(self):
        DailyImage.objects.create(
            user=self.user, filename='daily/pic.png', url='https://example.com/pic.png')

        response = self.client_api.get('/api/galleries/daily')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['image']['url'], 'https://example.com/pic.png')

    @mock.patch('scuba.galleries.models.FileUtils.upload_file_to_s3')
    def test_media_upload(self, mock_upload):
        response = self.client_api.post(
            '/api/galleries/media/', {'photo': _make_image_file()}, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['media']), 1)
        mock_upload.assert_called_once()
