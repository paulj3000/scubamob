from datetime import datetime, timedelta
import random
import decimal
from mimetypes import guess_extension

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from scuba.accounts.models import *
from scuba.libs.fileutils import FileUtils
from scuba.libs.stringutils import StringUtils


class UserListSerializer(serializers.Serializer):
    id = serializers.CharField()
    profile_image = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_image(data):
        return data.get_profile_image()

    @staticmethod
    def get_full_name(data):
        return data.get_full_name()

    @staticmethod
    def get_first_name(data):
        return data.first_name


class UploadFileListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        retval = []
        for data in validated_data:
            file = data.get('file')
            userid = data.get('userid')

            # generate a new filename, get content type, extensions,
            # etc.
            s3_name = StringUtils.generate_time_based_random_string(8)
            filename = file.name
            content_type = file.content_type
            ext = guess_extension(content_type)
            s3_name = f'chat/_temp/{s3_name}{ext}'

            # feed all of the data into the headers being sent over to S3
            s3_headers = {
                'headers': {
                    'ContentDisposition': f'attachment; filename={filename}',
                    'Metadata': {
                        'userid': userid,
                        'filename': filename
                     }
                },
            }

            # send over to S3 and append the new filename to the return value
            FileUtils.upload_file_to_s3(s3_name, content_type, file.read(), **s3_headers)
            retval.append({'s3file': s3_name})

        # and return...
        return retval


class UploadFileSerializer(serializers.Serializer):
    userid = serializers.CharField(write_only=True)
    file = serializers.FileField(use_url=False, write_only=True)
    s3file = serializers.CharField(read_only=True)

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        return UploadFileListSerializer(*args, **kwargs)
