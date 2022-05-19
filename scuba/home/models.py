from django.db import models
from django.templatetags.static import static

from scuba.libs.models.uuidmodel import UUIDModel


class HomeVideo(UUIDModel):
    """ UserProfileImage

    Keep a representation of the user's profile image
    """
    name = models.CharField(max_length=128)
    video = models.CharField(max_length=128)
    is_active = models.BooleanField(default=False)

    class Meta:
        """ define database tables, etc """
        db_table = 'home_video'

    def __str__(self):
        """ return a string representation of the model """
        return self.name

    @property
    def image_cleaned(self):
        return self.image.replace('programs/', '')

    @property
    def url(self):
        return static(self.video)

    @staticmethod
    def get_active_video(self):
        """ get_active_video

        Get the active video.
        * If one exists, return the full URL
        * If not, return None
        """
        try:
            return HomeVideo.objects.get(is_active=True).url
        except HomeVideo.DoesNotExist:
            return None
