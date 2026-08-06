"""
Tests for scuba.libs.fileutils.FileUtils.upload_file_to_s3. S3 calls are
mocked -- no live AWS access.
"""
from unittest.mock import patch

from django.test import SimpleTestCase

from scuba.libs.fileutils import FileUtils
from scuba.settings import AWS_S3_BUCKET


class TestFileUtils(SimpleTestCase):
    @patch('scuba.libs.fileutils.S3.upload_raw_data')
    def test_upload_file_to_s3_calls_the_real_s3_method(self, mock_upload):
        FileUtils.upload_file_to_s3('content/report.txt', 'text/plain', b'hello world')

        mock_upload.assert_called_once_with(
            'content/report.txt', b'hello world', bucket=AWS_S3_BUCKET,
            ContentType='text/plain')

    @patch('scuba.libs.fileutils.S3.upload_raw_data')
    def test_upload_file_to_s3_merges_extra_headers(self, mock_upload):
        FileUtils.upload_file_to_s3(
            'content/report.txt', 'text/plain', b'hello world',
            headers={'ACL': 'public-read'})

        mock_upload.assert_called_once_with(
            'content/report.txt', b'hello world', bucket=AWS_S3_BUCKET,
            ContentType='text/plain', ACL='public-read')
