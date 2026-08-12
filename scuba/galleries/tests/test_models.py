from io import BytesIO
from unittest import mock

from PIL import Image as PILImage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from scuba.accounts.models import User
from scuba.galleries.models import Album, AlbumImage, AlbumMedia, Media


def _make_image_file(name='test.png', content_type='image/png'):
    buf = BytesIO()
    PILImage.new('RGB', (20, 20)).save(buf, format='PNG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type=content_type)


class TestAlbumModel(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')
        self.album = Album.objects.create(user=self.user, title='My Trip')

    def test_to_json_uses_real_pk_as_guid(self):
        json = self.album.to_json()

        self.assertEqual(json['id'], self.album.id)
        self.assertEqual(json['guid'], self.album.pk_as_str)

    @mock.patch('scuba.galleries.models.S3.upload_raw_data')
    def test_add_image_uploads_and_returns_key(self, mock_upload):
        uploaded = _make_image_file()

        key = self.album.add_image(uploaded)

        self.assertIn(self.user.pk_as_str, key)
        self.assertIn(self.album.pk_as_str, key)
        mock_upload.assert_called_once()

    @mock.patch('scuba.galleries.models.S3.upload_raw_data')
    def test_add_image_thumbnail_uploads_and_returns_key(self, mock_upload):
        uploaded = _make_image_file()

        key = self.album.add_image_thumbnail(uploaded)

        self.assertIn('p206x206', key)
        mock_upload.assert_called_once()

    @mock.patch('scuba.galleries.models.S3.upload_raw_data')
    def test_full_image_upload_roundtrip_creates_album_image(self, mock_upload):
        uploaded = _make_image_file()

        full_key = self.album.add_image(uploaded)
        thumb_key = self.album.add_image_thumbnail(uploaded)

        album_image = AlbumImage.objects.create(
            album=self.album, image=full_key, thumbnail=thumb_key)

        self.assertEqual(album_image.get_image(), settings_prod_url() + full_key)
        self.assertEqual(album_image.get_thumbnail(), settings_prod_url() + thumb_key)


def settings_prod_url():
    from scuba.settings import PRODUCTION_GALLERY_URL
    return PRODUCTION_GALLERY_URL


class TestMediaModel(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')

    @mock.patch('scuba.galleries.models.FileUtils.upload_file_to_s3')
    def test_upload_new_media_creates_media_with_user(self, mock_upload):
        media = Media.upload_new_media(self.user, 'my photo.png', 'image/png', b'data')

        self.assertEqual(media.user, self.user)
        self.assertTrue(media.filename.startswith('content/'))
        mock_upload.assert_called_once()

    @mock.patch('scuba.galleries.models.FileUtils.upload_file_to_s3')
    def test_upload_new_media_dedupes_title(self, mock_upload):
        first = Media.upload_new_media(self.user, 'photo', 'image/png', b'data')
        second = Media.upload_new_media(self.user, 'photo', 'image/png', b'data')

        self.assertNotEqual(first.title, second.title)

    def test_get_image_and_thumbnail_use_real_fields(self):
        media = Media.objects.create(
            user=self.user, filename='content/1/pic.png', title='pic', thumbnail='thumb.png')

        self.assertEqual(media.get_image(), settings_prod_url() + 'content/1/pic.png')
        self.assertEqual(media.get_thumbnail(), settings_prod_url() + 'thumb.png')


class TestAlbumMediaModel(TestCase):
    fixtures = ["test_users.json"]

    def test_album_media_points_at_media_not_album(self):
        user = User.objects.get(email='foo@nowhere.com')
        album = Album.objects.create(user=user, title='Trip')
        media = Media.objects.create(user=user, filename='content/1/pic.png', title='pic')

        album_media = AlbumMedia.objects.create(album=album, media=media, pos=0)

        self.assertEqual(album_media.media, media)
        self.assertIn(album_media, media.albums.all())


class TestAlbumDeleteSignal(TestCase):
    fixtures = ["test_users.json"]

    @mock.patch('scuba.galleries.signals.S3.delete_file')
    @mock.patch('scuba.galleries.models.S3.upload_raw_data')
    def test_deleting_album_deletes_its_images_from_s3(self, mock_upload, mock_delete):
        user = User.objects.get(email='foo@nowhere.com')
        album = Album.objects.create(user=user, title='Trip')
        AlbumImage.objects.create(album=album, image='full.png', thumbnail='thumb.png')

        album.delete()

        self.assertEqual(mock_delete.call_count, 2)
        deleted_keys = {call.args[0] for call in mock_delete.call_args_list}
        self.assertEqual(deleted_keys, {'full.png', 'thumb.png'})
