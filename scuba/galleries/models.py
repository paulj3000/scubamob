import os
import uuid
from PIL import Image
from io import BytesIO

from django.db import models

import scuba.settings as settings
from scuba.accounts.models import User
from scuba.libs.fileutils import FileUtils
from scuba.libs.models.awsmodel import AWSModel
from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.stringutils import StringUtils
from scuba.libs.aws.s3 import S3


IMAGE_TYPE_EXTENSIONS = {
        'image/gif': 'gif',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/tiff': 'tiff'
}

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB


class Media(UUIDModel):
    user = models.ForeignKey(User, related_name='media', on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    # define a couple of static functions which will define an image name
    @staticmethod
    def generate_image_name(guid, album_id, filename):
        # generate a new filename
        return '%s/%s/%s' % (guid, album_id, filename)

    @staticmethod
    def generate_image_thumbnail_name(guid, album_id, filename):
        # generate a new filename
        return '%s/%s/p206x206/%s' % (guid, album_id, filename)

    def get_image(self):
        return settings.PRODUCTION_GALLERY_URL + self.filename

    def get_thumbnail(self):
        return settings.PRODUCTION_GALLERY_URL + self.thumbnail

    class Meta:
        db_table = 'media'

    @staticmethod
    def upload_new_media(user, name, content_type, data):
        title = StringUtils.generate_url_from_string(name)

        count = Media.objects.filter(title=title).count()
        extra = 1
        while count:
            tmp_name, ext = os.path.splitext(title)
            title = f"{tmp_name}-{extra}{ext}"
            extra += 1
            count = Media.objects.filter(title=title).count()

        # TODO: validate the extension
        aws_filename = f"content/{settings.SITE_ID}/{title}"

        # upload the file to s3
        FileUtils.upload_file_to_s3(aws_filename, content_type, data)

        # and now, create the file
        return Media.objects.create(user=user, filename=aws_filename, title=title)


class Album(UUIDModel):
    user = models.ForeignKey(User, related_name='albums', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def guid(self):
        return self.pk_as_str

    def add_image(self, uploaded_image):
        # seek to the beginning of the script
        filename = "%s.%s" % (
            str(uuid.uuid1()).replace('-', ''),
            IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type])

        name = AlbumImage.generate_image_name(self.user.pk_as_str, self.pk_as_str, filename)
        headers = {'Content-Type': uploaded_image.content_type}

        S3.upload_raw_data(name, uploaded_image.read(), bucket=settings.GALLERY_BUCKET, **headers)
        return name

    def add_image_thumbnail(self, uploaded_image):
        # this is really bad!  Refactor
        uploaded_image.seek(0)

        filename = "%s.%s" % (
            str(uuid.uuid1()).replace('-', ''),
            IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type])

        gallery_file_thumbnail = AlbumImage.generate_image_thumbnail_name(
            self.user.pk_as_str, self.pk_as_str, filename)
        headers = {'Content-Type': uploaded_image.content_type}

        WHITE = (255, 255, 255)

        size = 150, 150
        im = Image.open(BytesIO(uploaded_image.read()))
        im.thumbnail(size, Image.LANCZOS)

        bg = Image.new('RGB', (150, 150), WHITE)

        W, H = bg.size
        w, h = im.size

        xo, yo = (W - w) // 2, (H - h) // 2
        bg.paste(im, (xo, yo, xo + w, yo + h))

        # convert the image
        img_type = IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type]
        img_type = 'jpeg' if img_type.lower() == 'jpg' else img_type

        temp_handle = BytesIO()
        bg.save(temp_handle, img_type)
        temp_handle.seek(0)

        S3.upload_raw_data(gallery_file_thumbnail,
                           temp_handle.read(),
                           bucket=settings.GALLERY_BUCKET,
                           **headers)

        return gallery_file_thumbnail

    class Meta:
        db_table = 'gallery_album'

    def to_json(self):
        return {
            'title': self.title, 'description': self.description,
            'id': self.id, 'guid': self.pk_as_str}


class AlbumImage(UUIDModel):
    album = models.ForeignKey(Album, related_name='album_image', on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255)
    guid = models.CharField(max_length=125, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # define a couple of static functions which will define an image name
    @staticmethod
    def generate_image_name(guid, album_id, filename):
        # generate a new filename
        return '%s/%s/%s' % (guid, album_id, filename)

    @staticmethod
    def generate_image_thumbnail_name(guid, album_id, filename):
        # generate a new filename
        return '%s/%s/p206x206/%s' % (guid, album_id, filename)

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


class AlbumMedia(UUIDModel):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, related_name='albums', on_delete=models.CASCADE)
    pos = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = 'album media'
        db_table = 'album_media'


class DailyImage(AWSModel):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'daily images'
        db_table = 'daily_image'
