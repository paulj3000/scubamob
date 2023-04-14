from django.db import models
from django.templatetags.static import static

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.divesites.settings import REVIEW_CHOICES, DIFFICULTY_CHOICES
from scuba.libs.stringutils import StringUtils
from scuba.sitesettings.models import SystemSetting
from scuba.settings import AWS_CLOUDFRONT


class Divesite(UUIDModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField(max_length=255, db_index=True, blank=True)
    lat = models.DecimalField(max_digits=15, decimal_places=9)
    long = models.DecimalField(max_digits=15, decimal_places=9)
    is_active = models.BooleanField(default=True)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES)

    class Meta:
        db_table = 'divesites'

    def __str__(self):
        return self.name

    @property
    def banner(self):
        return self.get_banner()

    def save(self, *args, **kwargs):
        # generate a url for the divesite
        self.url = StringUtils.generate_url_from_string(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def get_all_active_divesites():
        return Divesite.objects.filter(is_active=True)

    # -----------------------------------------------------------------------------
    # start banner image stuff
    # -----------------------------------------------------------------------------
    def get_banner(self):
        """ get_banner

        return a banner for the divesite. If one does not exist, get a blank / default
        one
        """
        if hasattr(self, 'divesitebanner'):
            return self.divesitebanner.get_banner_image()

        # No profile image. just return a default
        return static(SystemSetting.get_default_banner_image())


class DivesiteReview(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='reviews', on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=REVIEW_CHOICES)
    review_date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'divesite_reviews'
        unique_together = (('user', 'divesite', 'review_date'), )


class DivesiteBanner(UUIDModel):
    divesite = models.OneToOneField(Divesite, on_delete=models.CASCADE)
    banner = models.CharField(max_length=128)

    class Meta:
        db_table = 'divesite_banner'

    @property
    def image_cleaned(self):
        return self.image.replace('programs/', '')

    def get_banner_image(self):
        """ get_banner_image

        sanitize the profile image. This will return the full url path
        of the profile image, sans the 'profiles/' prefix
        """
        return f"{AWS_CLOUDFRONT}{self.image_cleaned}"


class DivesiteFollowing(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='followers', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='following', on_delete=models.CASCADE)
    is_following = models.BooleanField(default=True)

    class Meta:
        db_table = 'divesite_following'
