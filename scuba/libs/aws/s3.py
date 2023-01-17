"""
# cfk/libs/aws/s3.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Some utility methods to upload stuff and download stuff from / to AWS
"""
import os

import json
import boto3
import botocore

from botocore.exceptions import ClientError


class S3:
    """ S3

    Here are some simple functions to interact w/ AWS's S3.

    A lot of these functions are now staticmethods, but some of them are still
    using class instantiation.
    """
    @staticmethod
    def get_session(aws_profile='default', **kwargs):
        """ get session

        This will create a session which will connect to S3 by
        way of our profile id
        """
        if os.getenv('DEBUG'):
            return boto3.client('s3')

        session = boto3.Session(profile_name=aws_profile)

        if kwargs.get('region'):
            return session.resource('s3', region_name=kwargs['region'])

        return session.resource('s3')

    @staticmethod
    def list_all_buckets():
        """ list all buckets

        return a list of all the buckets available to this account
        """
        retval = []
        s3 = boto3.client('s3')

        response = s3.list_buckets()

        for bucket in response['Buckets']:
            retval.append(bucket['Name'])

        # return the bucket list
        return retval

    @staticmethod
    def list_bucket_contents(bucket, prefix=None):
        """ list_all_files

        Get a list of all of the files from S3
        """
        # get the bucket
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket)

        retval = []

        files = None
        if prefix:
            files = bucket.objects.filter(Prefix=prefix)
        else:
            files = bucket.objects.all()

        for file in files:
            retval.append(file.key)

        return retval

    @staticmethod
    def verify_file(key, bucket):
        """ verify_file

        Verify a file exists.
        """
        # get the bucket
        session = S3.get_session()

        try:
            return session.Object(bucket, key)
        except botocore.exceptions.ClientError:
            return None

        return None

    @staticmethod
    def upload_file_content(bucket, key, fileobj, **headers):
        """ Upload raw data to Amazon S3. Pass in the name, the actual
        object, and optionally extra data metadata"""
        to_send = {
            'Key': key,
            'Body': fileobj,
        }

        # set any additional header items which were passed in
        for key, val in headers.items():
            to_send[key] = val

        s3 = boto3.resource('s3')
        return s3.Bucket(bucket).put_object(**to_send)

    @staticmethod
    def delete_file(bucket, key):
        """ delete_file

        Delete the file from S3
        """
        s3 = boto3.resource('s3')
        return s3.Object(bucket, key).delete()

    @staticmethod
    def get_file_headers(bucket, key):
        s3 = boto3.resource('s3')

        try:
            obj = s3.Object(bucket, key)

            retval = {}
            temp = {
                'content_disposition': obj.content_disposition,
                'content_type': obj.content_type,
                'metadata': obj.metadata
            }

            for key, value in temp.items():
                if value:
                    retval[key] = value

            return retval

        except botocore.exceptions.ClientError:
            raise AWS404Exception

    def upload_data(self, name, data, **kwargs):
        """ upload_data

        Uplaod raw data from a data source to S3
        """
        kwargs['Key'] = name
        kwargs['Body'] = data
        self.bucket_obj.put_object(**kwargs)

    def upload_file(self, filename, name, **headers):
        """ Upload a file from filename """
        to_send = {}

        # set any additional header items which were passed in
        for key, val in headers.items():
            to_send[key] = val

        self.bucket_obj.upload_file(filename, name, to_send)

    @staticmethod
    def get_file_metadata(bucket, key):
        s3_obj = S3.get_session()

    @staticmethod
    def rename_file(bucket, old_name, new_name):
        """ rename_file

        Rename a file on S3
        """
        s3 = boto3.resource('s3')
        s3.Object(bucket, new_name).copy_from(CopySource=f"{bucket}/{old_name}")
        s3.Object(bucket, old_name).delete()

    @staticmethod
    def upload_public_file(bucket, filename, key, **kwargs):
        """ upload_public_file

        Upload a file to the public (normal) bucket.
        """
        s3_obj = S3.get_session()
        bucket_obj = s3_obj.Bucket(bucket)
        bucket_obj.upload_file(filename, key, kwargs)

    @staticmethod
    def create_bucket(bucket_name, region=None):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """
        # Create bucket
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

# https://aws.amazon.com/blogs/compute/uploading-to-amazon-s3-directly-from-a-web-or-mobile-application/
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
