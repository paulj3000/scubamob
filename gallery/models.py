from pprint import pprint
import re
import uuid
import datetime
from PIL import Image
import cStringIO
from StringIO import StringIO

from django.db import models
from django.db.models import fields, Q
from django.contrib.auth.models import User
from django.conf import settings 
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from boto.s3.connection import S3Connection

from utils import uuidmodel
from utils.core.models import Timestamped

IMAGE_TYPE_EXTENSIONS   = {
        'image/gif': 'gif',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/tiff': 'tiff'
}

class Album(Timestamped, models.Model):
    user = models.ForeignKey(User, related_name='albums' )
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    guid = models.CharField(max_length=125, db_index=True)

    def add_image(self, uploaded_image):
        ### seek to the beginning of the script
        #uploaded_image.seek(0)
        filename    = "%s.%s" % (str(uuid.uuid1()).replace('-', ''), 
                    IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type])

        account     = self.user.get_account()
        gallery_file            = AlbumImage.generate_image_name(account.guid, self.guid, filename)
        header = {'Content-Type' : uploaded_image.content_type}

        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket(settings.GALLERY_BUCKET)

        k = b.new_key(gallery_file)
        k.set_contents_from_string(uploaded_image.read(), header)
   
        return gallery_file

    def add_image_thumbnail(self, uploaded_image):
        ###### this is really bad!  Refactor
        uploaded_image.seek(0)

        filename    = "%s.%s" % (str(uuid.uuid1()).replace('-', ''), 
                    IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type])

        account     = self.user.get_account()
        gallery_file_thumbnail  = AlbumImage.generate_image_thumbnail_name(account.guid, self.guid, filename)
        header = {'Content-Type' : uploaded_image.content_type}

        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket(settings.GALLERY_BUCKET)

        WHITE   = (255, 255, 255)

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

        ### convert the image
        img_type   = IMAGE_TYPE_EXTENSIONS[uploaded_image.content_type]
        img_type    = 'jpeg' if img_type.lower() == 'jpg' else img_type

        temp_handle = StringIO()
        bg.save(temp_handle, img_type)
        temp_handle.seek(0)

        k.set_contents_from_string(temp_handle.read(), header)

        return gallery_file_thumbnail

    def save(self, *args, **kwargs):
        ## save the album

        if not self.guid:
            self.guid    = str(uuid.uuid1()).replace('-', '')

        super(Album, self).save(*args, **kwargs)
   
    def delete(self):
        pprint(self.album_image.all())
        #super(Album, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'gallery_album'

    def to_json(self):
        return { 'title': self.title, 'description': self.description, 'id': self.id, 'guid': self.guid }

class AlbumImage(Timestamped, models.Model):
    album = models.ForeignKey(Album, related_name='album_image')
    image = models.CharField(max_length=255)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255)
    guid = models.CharField(max_length=125, db_index=True)

    ### define a couple of static functions which will define an image name
    @staticmethod
    def generate_image_name(guid, album_id, filename):
        ### generate a new filename
        return  '%s/%s/%s' % (guid, album_id, filename)
    
    @staticmethod
    def generate_image_thumbnail_name(guid, album_id, filename):
        ### generate a new filename
        return  '%s/%s/p206x206/%s' % (guid, album_id, filename)


    def save(self, *args, **kwargs):
        ## save the album

        if not self.guid:
            self.guid    = str(uuid.uuid1()).replace('-', '')

        super(AlbumImage, self).save(*args, **kwargs)
    
    def get_image(self):
        return settings.PRODUCTION_GALLERY_URL + self.image
    
    def get_thumbnail(self):
        return settings.PRODUCTION_GALLERY_URL + self.thumbnail

    class Meta:
        db_table = 'gallery_album_image'

## add a signal to delete the the images from S3 before we delete the album
@receiver(pre_delete, sender=Album)
def _mymodel_delete(sender, instance, **kwargs):
    images  = instance.album_image.all()

    ### MOVE THIS TO IT'S OWN LIBRARY
    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    b = conn.get_bucket(settings.GALLERY_BUCKET)

    ### delete the images   Eventually move this to SQS as we want to do this 
    ### offline
    to_delete   = []
    for i in images:
        ## append these images to the queue
        to_delete.append(i.image)
        to_delete.append(i.thumbnail)
   
    ### and finally delete them all
    result  = b.delete_keys(to_delete)
    result.deleted
