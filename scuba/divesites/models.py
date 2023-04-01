from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.divesites.settings import REVIEW_CHOICES, DIFFICULTY_CHOICES
from scuba.libs.stringutils import StringUtils


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

    def save(self, *args, **kwargs):
        # generate a url for the divesite
        self.url = StringUtils.generate_url_from_string(self.name)
        super().save(*args, **kwargs)


    @staticmethod
    def get_all_active_divesites():
        return Divesite.objects.filter(is_active=True)


class DivesiteReview(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='reviews', on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=REVIEW_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'divesite_reviews'


class DivesiteBanner(UUIDModel):
    divesite = models.OneToOneField(Divesite, on_delete=models.CASCADE)
    banner = models.CharField(max_length=128)

    class Meta:
        db_table = 'divesite_banner'
