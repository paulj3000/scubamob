from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete

from scuba.gallery.models import Media


# add a signal to delete the the images from S3 before we delete the album
@receiver(pre_delete, sender=Media)
def _mymodel_delete(sender, instance, **kwargs):
    images = instance.album_image.all()

    # MOVE THIS TO IT'S OWN LIBRARY
    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    b = conn.get_bucket(settings.GALLERY_BUCKET)

    # delete the images   Eventually move this to SQS as we want to do this
    # offline
    to_delete = []
    for i in images:
        # append these images to the queue
        to_delete.append(i.image)
        to_delete.append(i.thumbnail)

    # and finally delete them all
    result = b.delete_keys(to_delete)
    result.deleted
