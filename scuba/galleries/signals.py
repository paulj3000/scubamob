import boto3

from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete

from scuba.galleries.models import Media
from scuba.settings import (
    GALLERY_BUCKET
)


# add a signal to delete the the images from S3 before we delete the album
@receiver(pre_delete, sender=Media)
def _mymodel_delete(sender, instance, **kwargs):
    images = instance.album_image.all()

    # MOVE THIS TO IT'S OWN LIBRARY
    client = boto3.client('s3')

    # delete the images   Eventually move this to SQS as we want to do this
    # offline
    for i in images:
        client.delete_object(Bucket=GALLERY_BUCKET, Key=i.image)
        client.delete_object(Bucket=GALLERY_BUCKET, Key=i.thumbnail)
