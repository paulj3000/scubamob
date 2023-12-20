from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel


class AWSModel(UUIDModel):
    filename = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def __str__(self):
        return self.filename

    def delete(self):
        """ delete

        Before we delete the object, delete the object from S3
        """
        S3.delete_file(self.filename)
        super().delete()

    def upload_file(self, file, to_file, **kwargs):
        ''' use the aws file object to upload stuff to S3
        Params:
            file: the file on the local computer to upload
            to_file: the destination file
        '''
        cb = kwargs.get('cb')
        s3 = S3(settings.AWS_S3_BUCKET)
        s3.upload_from_filename(file, to_file, cb=cb)
