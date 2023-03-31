from django.db import models

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.divesites.settings import REVIEW_CHOICES, DIFFICULTY_CHOICES


class Divesite(UUIDModel):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=255)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES)

    class Meta:
        db_table = 'divesites'


class DivesiteReview(UUIDModel):
    divesite = models.ForeignKey(Divesite, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='reviews', on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=REVIEW_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'divesite_reviews'
