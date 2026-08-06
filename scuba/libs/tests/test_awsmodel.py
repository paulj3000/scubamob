"""
Tests for scuba.libs.models.awsmodel.AWSModel, exercised through the
concrete scuba.content.models.Image subclass. All S3 calls are mocked --
no live AWS access.
"""
from unittest.mock import patch

from django.test import TestCase

from scuba.content.models import Image


class TestAWSModel(TestCase):
    def setUp(self):
        self.image = Image.objects.create(filename='content/test-image.png', title='test')

    @patch('scuba.libs.models.awsmodel.S3.delete_file')
    def test_delete_removes_the_s3_object_then_the_row(self, mock_delete_file):
        self.image.delete()

        mock_delete_file.assert_called_once_with('content/test-image.png')
        self.assertFalse(Image.objects.filter(pk=self.image.pk).exists())

    @patch('scuba.libs.models.awsmodel.S3')
    def test_upload_file_uses_the_real_s3_upload_method(self, mock_s3_class):
        mock_s3_instance = mock_s3_class.return_value

        self.image.upload_file('/tmp/local-file.png', 'content/uploaded.png')

        mock_s3_class.assert_called_once()
        mock_s3_instance.upload_file.assert_called_once_with(
            '/tmp/local-file.png', 'content/uploaded.png')
