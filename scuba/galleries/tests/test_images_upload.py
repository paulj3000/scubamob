from io import BytesIO
from unittest import mock

from PIL import Image as PILImage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from scuba.accounts.models import User
from scuba.galleries.models import Album, AlbumImage


def _make_image_file(name='test.png', content_type='image/png'):
    buf = BytesIO()
    PILImage.new('RGB', (20, 20)).save(buf, format='PNG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type=content_type)


class TestGalleryImageUpload(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')
        self.other_user = User.objects.get(email='test2@tester.com')
        self.album = Album.objects.create(user=self.user, title='My Trip')
        self.client.force_login(self.user)

    @mock.patch('scuba.galleries.models.S3.upload_raw_data')
    def test_successful_upload_creates_album_image(self, mock_upload):
        response = self.client.post('/gallery/albums/image/upload', {
            'albumId': self.album.pk_as_str,
            'image': _make_image_file(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AlbumImage.objects.filter(album=self.album).count(), 1)
        self.assertEqual(mock_upload.call_count, 2)  # full image + thumbnail

    def test_upload_to_another_users_album_is_rejected(self):
        others_album = Album.objects.create(user=self.other_user, title='Not yours')

        response = self.client.post('/gallery/albums/image/upload', {
            'albumId': others_album.pk_as_str,
            'image': _make_image_file(),
        })

        self.assertEqual(response.status_code, 404)
        self.assertEqual(AlbumImage.objects.count(), 0)

    def test_unsupported_content_type_is_rejected(self):
        bad_file = SimpleUploadedFile('evil.txt', b'not an image', content_type='text/plain')

        response = self.client.post('/gallery/albums/image/upload', {
            'albumId': self.album.pk_as_str,
            'image': bad_file,
        })

        self.assertEqual(response.status_code, 400)

    def test_oversized_upload_is_rejected(self):
        with mock.patch('scuba.galleries.views.images.MAX_UPLOAD_SIZE', 10):
            response = self.client.post('/gallery/albums/image/upload', {
                'albumId': self.album.pk_as_str,
                'image': _make_image_file(),
            })

        self.assertEqual(response.status_code, 400)

    def test_corrupt_file_with_spoofed_content_type_is_rejected(self):
        spoofed = SimpleUploadedFile('fake.png', b'not really a png', content_type='image/png')

        response = self.client.post('/gallery/albums/image/upload', {
            'albumId': self.album.pk_as_str,
            'image': spoofed,
        })

        self.assertEqual(response.status_code, 400)

    def test_missing_params_is_rejected(self):
        response = self.client.post('/gallery/albums/image/upload', {})

        self.assertEqual(response.status_code, 400)
