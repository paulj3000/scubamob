import string
from random import choice

from django.db import models
from django.templatetags.static import static
from django.db.models import Avg, DateTimeField, ExpressionWrapper, F
from django.db.models.functions import Cast, Coalesce

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.divesites.settings import RATING_CHOICES, DIFFICULTY_CHOICES
from scuba.libs.stringutils import StringUtils
from scuba.libs.imageuploader import ImageUploader
from scuba.sitesettings.models import SystemSetting
from scuba.settings import AWS_CLOUDFRONT


class Divesite(UUIDModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField(max_length=255, db_index=True, blank=True)
    lat = models.DecimalField(max_digits=15, decimal_places=9)
    long = models.DecimalField(max_digits=15, decimal_places=9)
    aws_id = models.CharField(max_length=10, blank=True)
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

    def add_to_favorite(self, user):
        self.followers.create(user=user)

    @staticmethod
    def get_all_active_divesites():
        return Divesite.objects.filter(is_active=True)

    def get_aws_id(self):
        """ a small utility to validate we have a valid AWS id

        If the user does not have an AWS id, generate one for
        him then return it
        """
        if self.aws_id is None or self.aws_id == '':
            self.aws_id = self.generate_aws_id()
            self.save()

        # return the aws id
        return self.aws_id

    def generate_aws_id(self):
        ''' generate a unique aws id for a program '''
        letters_and_digits = string.ascii_letters + string.digits
        key_length = 7

        def gen():
            key = [choice(letters_and_digits) for i in range(key_length)]
            key = key[:2] + ['/'] + key[2:]

            # a quick little function to generate the key
            return 'dx' + ''.join(key)

        aws_id = gen()
        while Divesite.objects.filter(aws_id=aws_id).count():
            aws_id = gen()

        # return the generated id
        return aws_id

    def get_active_banner(self):
        banner = self.banners.filter(is_active=True).first()

        if banner:
            img = banner.image.replace('divesites/', '')
            return f"{AWS_CLOUDFRONT}{img}"

        return None


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

    def upload_banner(self, uploaded_image):
        """ upload_banner

        this will upload a new cover to the site, but before we do that,
        compress, resize, etc
        """
        # generate the key name
        path = f"divesites/{self.get_aws_id()}"
        filename = ImageUploader.compress_upload_image(uploaded_image, path)

        active = False
        if not self.get_active_image():
            active = True

        return self.banner.create(filename=filename, is_active=active)

    def get_active_banner(self):
        banner_image = self.banners.filter(is_active=True).first()

        if banner_image:
            img = banner_image.banner.replace('divesites/', '')
            return f"{AWS_CLOUDFRONT}{img}"

        return None

    def get_divesites_stats(self, date):
        return DivesiteDailyStats.objects.filter(divesite=self).aggregate(
            avg_temp_c = Coalesce(Avg('temp_c', output_field=models.IntegerField()), models.Value(0)),
            avg_temp_f = Coalesce(ExpressionWrapper(
            (
                Avg((F('temp_c') * (9/5)) + 32)
            ), output_field=models.IntegerField()), models.Value(0)),
            avg_visibility=Coalesce(Avg('visibility', output_field=models.IntegerField()), models.Value(0)))


class DivesiteReview(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='reviews', on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    review_date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'divesite_reviews'
        unique_together = (('user', 'divesite', 'review_date'), )


class DivesiteBanner(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='banners', on_delete=models.CASCADE)
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


class DivesiteFavorite(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='followers', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='favorites', on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=True)

    class Meta:
        db_table = 'divesite_favorite'


class DivesiteDailyStats(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='stats', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='stats', on_delete=models.CASCADE)
    temp_c = models.FloatField()
    visibility = models.PositiveSmallIntegerField()
    stats_date = models.DateField()

    class Meta:
        db_table = 'divesite_daily_stats'
