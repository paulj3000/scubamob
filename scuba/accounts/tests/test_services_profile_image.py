from io import BytesIO
from unittest import mock

from PIL import Image as PILImage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from scuba.accounts.exceptions import InvalidProfileImageException
from scuba.accounts.models import User, UserProfileImage
from scuba.accounts.services import profile_image


def _make_image_file(name='avatar.png', content_type='image/png', size=(20, 20), mode='RGB'):
    buf = BytesIO()
    PILImage.new(mode, size).save(buf, format='PNG' if content_type == 'image/png' else 'JPEG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type=content_type)


class TestSetProfileImage(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='avatar@nowhere.com', username='avataruser',
            password='tester1234', first_name='Avatar', last_name='User')

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_creates_a_new_profile_image(self, mock_upload):
        result = profile_image.set_profile_image(self.user, _make_image_file())

        self.assertIsInstance(result, UserProfileImage)
        self.assertEqual(result.user, self.user)
        self.assertTrue(result.image.startswith(f'profiles/{self.user.aws_id}/'))
        self.assertTrue(result.image.endswith('.png'))

        mock_upload.assert_called_once()
        args, kwargs = mock_upload.call_args
        self.assertEqual(args[0], result.image)
        self.assertEqual(kwargs['ContentType'], 'image/png')

    @mock.patch('scuba.accounts.services.profile_image.S3.delete_file')
    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_replaces_and_cleans_up_an_existing_profile_image(self, mock_upload, mock_delete):
        existing = UserProfileImage.objects.create(user=self.user, image='profiles/old/old.png')

        result = profile_image.set_profile_image(self.user, _make_image_file())

        self.assertEqual(result.pk, existing.pk)
        self.assertNotEqual(result.image, 'profiles/old/old.png')
        self.assertEqual(UserProfileImage.objects.filter(user=self.user).count(), 1)
        mock_delete.assert_called_once_with('profiles/old/old.png', bucket=mock.ANY)

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_unsupported_content_type_is_rejected(self, mock_upload):
        bad_file = SimpleUploadedFile('evil.txt', b'not an image', content_type='text/plain')

        with self.assertRaises(InvalidProfileImageException):
            profile_image.set_profile_image(self.user, bad_file)

        mock_upload.assert_not_called()
        self.assertFalse(UserProfileImage.objects.filter(user=self.user).exists())

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_oversized_upload_is_rejected(self, mock_upload):
        with mock.patch('scuba.accounts.services.profile_image.MAX_PROFILE_IMAGE_SIZE', 10):
            with self.assertRaises(InvalidProfileImageException):
                profile_image.set_profile_image(self.user, _make_image_file())

        mock_upload.assert_not_called()

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_corrupt_file_with_spoofed_content_type_is_rejected(self, mock_upload):
        spoofed = SimpleUploadedFile('fake.png', b'not really a png', content_type='image/png')

        with self.assertRaises(InvalidProfileImageException):
            profile_image.set_profile_image(self.user, spoofed)

        mock_upload.assert_not_called()

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_oversized_dimensions_are_downscaled(self, mock_upload):
        big_file = _make_image_file(size=(2000, 1000))

        profile_image.set_profile_image(self.user, big_file)

        uploaded_bytes = mock_upload.call_args[0][1]
        resized = PILImage.open(BytesIO(uploaded_bytes))
        self.assertLessEqual(max(resized.size), profile_image.PROFILE_IMAGE_MAX_DIMENSION)

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_transparent_png_declared_as_jpeg_is_flattened_not_crashed(self, mock_upload):
        # JPEG can't encode alpha, so this only bites when the declared
        # content type (used to pick the save format) doesn't match what
        # the bytes actually decode to -- exactly the case _prepare_image's
        # flatten-onto-white-background branch exists to handle safely.
        buf = BytesIO()
        PILImage.new('RGBA', (20, 20), (0, 0, 0, 0)).save(buf, format='PNG')
        buf.seek(0)
        upload = SimpleUploadedFile('transparent.png', buf.read(), content_type='image/jpeg')

        result = profile_image.set_profile_image(self.user, upload)

        self.assertTrue(result.image.endswith('.jpg'))
        uploaded_bytes = mock_upload.call_args[0][1]
        saved = PILImage.open(BytesIO(uploaded_bytes))
        self.assertEqual(saved.format, 'JPEG')
        self.assertEqual(saved.mode, 'RGB')
