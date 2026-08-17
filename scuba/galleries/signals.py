from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete

from scuba.galleries.models import Album
from scuba.libs.aws.s3 import S3
from scuba.settings import (
    GALLERY_BUCKET
)


# add a signal to delete the images from S3 before we delete the album
@receiver(pre_delete, sender=Album)
def _album_delete(sender, instance, **kwargs):
    images = instance.album_image.all()

    # delete the images. Eventually move this to SQS as we want to do this
    # offline
    for i in images:
        S3.delete_file(i.image, bucket=GALLERY_BUCKET)
        S3.delete_file(i.thumbnail, bucket=GALLERY_BUCKET)
