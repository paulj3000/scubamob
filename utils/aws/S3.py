from boto.s3.connection import S3Connection
from django.conf import settings


class S3:
    def __init__(self):
        self.conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket(settings.GALLERY_BUCKET)
        pass
