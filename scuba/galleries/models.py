from pprint import pprint
import re
import uuid
import datetime
from PIL import Image
from io import StringIO

from django.db import models
from django.db.models import fields, Q
from django.conf import settings

#from boto3.s3.connection import S3Connection

from scuba.accounts.models import User
from scuba.libs.fileutils import FileUtils

from utils import uuidmodel
from utils.core.models import Timestamped


IMAGE_TYPE_EXTENSIONS = {
        'image/gif': 'gif',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/tiff': 'tiff'
}


class Media(models.Model):
    user = models.ForeignKey(User, related_name='media', on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255)
    guid = models.CharField(max_length=125, db_index=True)

    # define a couple of static functions which will define an image name
    @staticmethod
    def generate_image_name(guid, album_id, filename):
        # generate a new filename
        return  '%s/%s/%s' % (guid, album_id, filename)

    @staticmethod
    def generate_image_thumbnail_name(guid, album_id, filename):
        # generate a new filename
        return  '%s/%s/p206x206/%s' % (guid, album_id, filename)

    def get_image(self):
        return settings.PRODUCTION_GALLERY_URL + self.image

    def get_thumbnail(self):
        return settings.PRODUCTION_GALLERY_URL + self.thumbnail

    class Meta:
        db_table = 'media'

    @staticmethod
    def upload_new_media(name, content_type, data):
        name = StringUtils.generate_url_from_string(name)
        print(name)

        count = Media.objects.filter(title=name).count()
        extra = 1
        while count:
            tmp_name, ext = os.path.splitext(name)
            tmp_name = f"{tmp_name}-{extra}{ext}"
            extra += 1
            count = Media.objects.filter(title=tmp_name).count()

            if not count:
                name = tmp_name

        # TODO: validate the extension
        #ext = guess_extension(content_type)
        #if not ext:
        #    raise InvalidContentTypeException(content_type)
        aws_filename = f"content/{SITE_ID}/{name}"

        # upload the file to s3
        FileUtils.upload_file_to_s3(aws_filename, content_type, data)

        # and now, create the file
        return Media.objects.create(filename=name, content_type=content_type, aws_filename=aws_filename)


class Album(Timestamped, models.Model):
    user = models.ForeignKey(User, related_name='albums', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    guid = models.CharField(max_length=125, db_index=True)

    def add_image(self, uploaded_image):
        # seek to the beginning of the script
        #uploaded_image.seek(0)
        filename = "%s.%s" % (str(uuid.uuid1()).replace('-', ''),
                    IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type])

        account = self.user.get_account()
        gallery_file = AlbumImage.generate_image_name(account.guid, self.guid, filename)
        header = {'Content-Type' : uploaded_image.content_type}

        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket(settings.GALLERY_BUCKET)

        k = b.new_key(gallery_file)
        k.set_contents_from_string(uploaded_image.read(), header)

        return gallery_file

    def add_image_thumbnail(self, uploaded_image):
        # this is really bad!  Refactor
        uploaded_image.seek(0)

        filename = "%s.%s" % (str(uuid.uuid1()).replace('-', ''),
                    IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type])

        account = self.user.get_account()
        gallery_file_thumbnail = AlbumImage.generate_image_thumbnail_name(account.guid, self.guid, filename)
        header = {'Content-Type' : uploaded_image.content_type}

        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket(settings.GALLERY_BUCKET)

        WHITE = (255, 255, 255)

        size = 150, 150
        im = Image.open(cStringIO.StringIO(uploaded_image.read()))
        im.thumbnail(size, Image.ANTIALIAS)

        bg = Image.new('RGB', (150, 150), WHITE)

        W, H = bg.size
        w, h = im.size

        xo, yo = (W-w)/2, (H-h)/2
        bg.paste(im, (xo, yo, xo+w, yo+h))

        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket(settings.GALLERY_BUCKET)
        k = b.new_key(gallery_file_thumbnail)

        # convert the image
        img_type = IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type]
        img_type = 'jpeg' if img_type.lower() == 'jpg' else img_type

        temp_handle = StringIO()
        bg.save(temp_handle, img_type)
        temp_handle.seek(0)

        k.set_contents_from_string(temp_handle.read(), header)

        return gallery_file_thumbnail

    def save(self, *args, **kwargs):
        # save the album

        if not self.guid:
            self.guid = str(uuid.uuid1()).replace('-', '')

        super(Album, self).save(*args, **kwargs)

    def delete(self):
        pprint(self.album_image.all())
        #super(Album, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'gallery_album'

    def to_json(self):
        return { 'title': self.title, 'description': self.description, 'id': self.id, 'guid': self.guid }


class AlbumImage(Timestamped, models.Model):
    album = models.ForeignKey(Album, related_name='album_image', on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255)
    guid = models.CharField(max_length=125, db_index=True)

    # define a couple of static functions which will define an image name
    @staticmethod
    def generate_image_name(guid, album_id, filename):
        # generate a new filename
        return  '%s/%s/%s' % (guid, album_id, filename)

    @staticmethod
    def generate_image_thumbnail_name(guid, album_id, filename):
        # generate a new filename
        return  '%s/%s/p206x206/%s' % (guid, album_id, filename)


    def save(self, *args, **kwargs):
        # save the album

        if not self.guid:
            self.guid = str(uuid.uuid1()).replace('-', '')

        super(AlbumImage, self).save(*args, **kwargs)

    def get_image(self):
        return settings.PRODUCTION_GALLERY_URL + self.image

    def get_thumbnail(self):
        return settings.PRODUCTION_GALLERY_URL + self.thumbnail

    class Meta:
        db_table = 'gallery_album_image'


class AlbumMedia(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    media = models.ForeignKey(Album, related_name='media', on_delete=models.CASCADE)
    pos = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = 'album media'
        db_table = 'album_media'
