from django.db import models
from django.templatetags.static import static

from scuba.libs.models.uuidmodel import UUIDModel


class HomeJumbotron(UUIDModel):
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
    def is_video(self):
        return True \
            if self.jumbotron_type == HomeJumbotron.JUMBOTRON_TYPE_VIDEO \
            else False

    @property
    def is_image(self):
        return True \
            if self.jumbotron_type == HomeJumbotron.JUMBOTRON_TYPE_IMAGE \
            else False

    @property
    def url(self):
        return static(self.filename)

    @staticmethod
    def get_active_jumbotron(self):
        """ get_active_video

        Get the active video.
        * If one exists, return the full URL
        * If not, return None
        """
        try:
            return HomeJumbotron.objects.get(is_active=True).url
        except HomeVideo.DoesNotExist:
            return None
