from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.divesites.settings import REVIEW_CHOICES, DIFFICULTY_CHOICES


class Divesite(UUIDModel):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=255, db_index=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    is_active = models.BooleanField(default=True)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES)

    class Meta:
        db_table = 'divesites'

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
