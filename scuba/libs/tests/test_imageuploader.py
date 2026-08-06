"""
Tests for scuba.libs.imageuploader.ImageUploader. All S3 calls are mocked
-- no live AWS access.
"""
from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase
from PIL import Image as PILImage

from scuba.libs.imageuploader import ImageUploader
from scuba.settings import AWS_S3_BUCKET


def _test_png_bytes():
    buf = BytesIO()
    PILImage.new('RGB', (400, 400), color='red').save(buf, format='PNG')
    buf.seek(0)
    return buf


class TestImageUploader(SimpleTestCase):
    @patch('scuba.libs.imageuploader.S3.upload_raw_data')
    def test_upload_file_passes_arguments_in_the_right_order(self, mock_upload):
        image_file = _test_png_bytes()

        filename = ImageUploader.upload_file(image_file, 'divesites/abc123', 'jpeg')

        self.assertTrue(filename.startswith('divesites/abc123/img_'))
        self.assertTrue(filename.endswith('.jpg'))

        args, kwargs = mock_upload.call_args
        # regression check for the swapped-argument bug: name must be the
        # generated S3 key, fileobj must be the actual file, not a string
        self.assertEqual(args[0], filename)
        self.assertIs(args[1], image_file)
        self.assertEqual(kwargs['bucket'], AWS_S3_BUCKET)
        self.assertEqual(kwargs['ContentType'], 'image/jpeg')

    @patch('scuba.libs.imageuploader.S3.upload_raw_data')
    def test_compress_upload_image_thumbnails_and_uploads_raw_plus_compressed(self, mock_upload):
        image_file = _test_png_bytes()

        filename = ImageUploader.compress_upload_image(image_file, 'divesites/abc123')

        self.assertTrue(filename.startswith('divesites/abc123/img_'))
        self.assertTrue(filename.endswith('.png'))
        # one upload for the raw original, one for the compressed thumbnail
        self.assertEqual(mock_upload.call_count, 2)
