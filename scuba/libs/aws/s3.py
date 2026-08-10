"""
# scuba/libs/aws/s3.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Some utility methods to upload stuff and download stuff from / to AWS
"""
import os
import boto3
from botocore.exceptions import ClientError

from scuba.settings import AWS_PROFILE, AWS_S3_BUCKET
from scuba.libs.exceptions import InvalidAWSKey


class S3:
    """ S3

    Here are some simple functions to interact w/ AWS's S3.

    A lot of these functions are now staticmethods, but some of them are still
    using class instantiation.
    """
    def __init__(self, bucket_name):
        # use the same credential resolution as get_session() (env vars
        # first, falling back to a local named AWS CLI profile) so this
        # works in containers/CI, not just a machine with
        # ~/.aws/credentials configured.
        self.conn = S3.get_session()

        # now assign the bucket
        self.bucket = bucket_name
        self.bucket_obj = self.conn.Bucket(bucket_name)

    @staticmethod
    def get_session():
        """ get session

        This will create a session which will connect to S3 by
        way of our profile id
        """
        session = None
        if os.getenv('AWS_SECRET_ACCESS_KEY') and os.getenv('AWS_ACCESS_KEY_ID'):
            session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
        else:
            session = boto3.Session(profile_name=AWS_PROFILE)

        return session.resource('s3')

    @staticmethod
    def list_all_files(bucket=AWS_S3_BUCKET):
        """ list_all_files

        Get a list of all of the files from S3
        """
        # get the bucket
        session = S3.get_session()
        bucket_obj = session.Bucket(bucket)

        # and return the list
        return bucket_obj.objects.all()

    @staticmethod
    def upload_raw_data(name, fileobj, bucket=AWS_S3_BUCKET, **headers):
        """ Upload raw data to Amazon S3. Pass in the name, the actual
        object, and optionally extra data metadata"""
        to_send = {
            'Key': name,
            'Body': fileobj,
        }

        # set any additional header items which were passed in
        for key, val in headers.items():
            to_send[key] = val

        session = S3.get_session()
        session.Bucket(bucket).put_object(**to_send)

    @staticmethod
    def delete_file(filename, bucket=AWS_S3_BUCKET):
        """ delete_file

        Delete the file from S3
        """
        s3_obj = S3.get_session()
        obj = s3_obj.Object(bucket, filename)
        obj.delete()

    @staticmethod
    def get_object(key, bucket=AWS_S3_BUCKET):
        """ get_file

        Get the file from S3
        """
        to_send = {
            'Key': key,
        }

        session = S3.get_session()

        try:
            obj = session.Object(bucket, key).get()
            return obj['Body']
        except ClientError:
            raise InvalidAWSKey

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
    def rename_file(old_name, new_name, bucket=AWS_S3_BUCKET):
        """ rename_file

        Rename a file on S3
        """
        s3_obj = S3.get_session()
        s3_obj.Object(bucket, new_name).copy_from(CopySource=f"{bucket}/{old_name}")
        s3_obj.Object(bucket, old_name).delete()

    @staticmethod
    def upload_public_file(filename, key, **kwargs):
        """ upload_public_file

        Upload a file to the public (normal) bucket.
        """
        s3_obj = S3.get_session()
        bucket_obj = s3_obj.Bucket(AWS_S3_BUCKET)
        bucket_obj.upload_file(filename, key, kwargs)
