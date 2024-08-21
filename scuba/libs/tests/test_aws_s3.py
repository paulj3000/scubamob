"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import pytest
from django.test import TestCase

from scuba.libs.aws.s3 import S3
from scuba.libs.stringutils import StringUtils
from scuba.libs.exceptions import InvalidAWSKey


class TestS3(TestCase):
    @pytest.mark.skip(reason="This is no longer valid")
    def test_list_all_files(self):
        """
        Test if a value is a float
        """
        file_list = {}
        test_dir = f'testing_{StringUtils.generate_time_string()}'

        for i in range(0, 10):
            key = f'{test_dir}/file_{i}.txt'
            S3.upload_raw_data(key, b'this is a test %d' % i)
            file_list[key] = False

        files = S3.list_all_files()
        for file in files:
            key = file.key
            if key in file_list:
                file_list[key] = True

        # verify the files have been uploaded
        for value in file_list.values():
            self.assertTrue(value)

        # verify the files exist
        for key in file_list.keys():
            self.assertIsNotNone(S3.get_object(key))
            S3.delete_file(key)

        # now verify the files are deleted
        for key in file_list.keys():
            with pytest.raises(InvalidAWSKey):
                S3.get_object(key)

    @pytest.mark.skip(reason="This is no longer valid")
    def test_rename_file(self):
        """
        Rename a file
        """
        test_dir = f'testing_{StringUtils.generate_time_string()}'

        key = f'{test_dir}/old_file.txt'
        new_key = f'{test_dir}/new_file.txt'
        S3.upload_raw_data(key, b'this is a test')
        S3.rename_file(key, new_key)

        # verify the file exist
        self.assertIsNotNone(S3.get_object(new_key))
        S3.delete_file(new_key)

        # now verify the file is deleted
        with pytest.raises(InvalidAWSKey):
            S3.get_object(new_key)
