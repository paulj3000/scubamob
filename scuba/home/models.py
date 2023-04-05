import os
import time
from urllib.parse import urljoin

from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from mimetypes import guess_extension

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.exceptions import InvalidContentTypeException
from scuba.libs.fileutils import FileUtils
from scuba.settings import (
    VIDEO_TYPES, IMAGE_TYPES, VALID_CONTENT_TYPES, AWS_CLOUDFRONT
)


class Jumbotron(UUIDModel):
    """ UserProfileImage

    Keep a representation of the user's profile image
    """
    JUMBOTRON_TYPE_VIDEO = 0
    JUMBOTRON_TYPE_IMAGE = 1

    JUMBOTRON_TYPE = (
        (0, 'Video'),
        (1, 'Image'),
    )
    name = models.CharField(max_length=128)
    filename = models.CharField(max_length=128)
    jumbotron_type = models.PositiveSmallIntegerField(choices=JUMBOTRON_TYPE)
    is_active = models.BooleanField(default=False)

    class Meta:
        """ define database tables, etc """
        db_table = 'home_jumbotron'

    def __str__(self):
        """ return a string representation of the model """
        return self.name

    @property
    def url(self):
        """ url

        return the filename with cloudfront attached to it
        """
        return urljoin(AWS_CLOUDFRONT, self.filename)

    @property
    def is_video(self):
        return True \
            if self.jumbotron_type == Jumbotron.JUMBOTRON_TYPE_VIDEO \
            else False

    @property
    def is_image(self):
        return True \
            if self.jumbotron_type == Jumbotron.JUMBOTRON_TYPE_IMAGE \
            else False

    def set_active(self):
        Jumbotron.objects.all().update(is_active=False)
        self.is_active = True
        self.save()

    @staticmethod
    def get_active_jumbotron():
        """ get_active_video

        Get the active video.
        * If one exists, return the full URL
        * If not, return None
        """
        try:
            return Jumbotron.objects.get(is_active=True)
        except Jumbotron.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            # we have more than one is_active. Fix
            jumbo = Jumbotron.objects.all().first()
            jumbo.set_active()
            return jumbo

    @staticmethod
    def upload_jumbotron(name, content_type, data):
        # TODO: validate the extension
        ext = guess_extension(content_type).lower().replace('.', '')
        if content_type not in VALID_CONTENT_TYPES:
            raise InvalidContentTypeException(content_type)

        extra = 1
        #_, ext = os.path.splitext(name)

        prefix = None
        jtron_type = None

        if ext.lower() in VIDEO_TYPES:
            jtron_type = Jumbotron.JUMBOTRON_TYPE_VIDEO
            prefix = 'vid'
        else:
            jtron_type = Jumbotron.JUMBOTRON_TYPE_IMAGE
            prefix = 'img'

        filename = f"jtrons/{prefix}_{int(time.time())}.{ext}"

        # upload the file to s3
        FileUtils.upload_file_to_s3(filename, content_type, data)

        return filename, jtron_type
