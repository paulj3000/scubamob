# -----------------------------------------------------------------------------
# scuba/logbook/forms.py
#
# This is the main class for the migrator.  This will take in a username, and
# an optional new username. The result will dictate whether the account can
# successfully be migrated
#
# (C) Copyright 2013, Divespot. All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django import forms

from .models import DivesiteReview


CLASSIFICATION_CHOICES = (
    ('shark', 'Shark'), ('reef', 'Reef'), ('wall', 'Wall'),
    ('wreck', 'Wreck'), ('drift', 'Drift'), ('dropoff', 'Drop Off'),
    ('muck', 'Muck'), ('cave', 'Cave'), ('ice', 'Ice'), ('night', 'Night'),
    ('rock', 'Rock'), ('deep', 'Deep'), ('inland', 'Inland'), ('other', 'Other'))


class DivesiteReviewForm(forms.ModelForm):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass

    class Meta:
        model = DivesiteReview
        exclude = ('user', 'divesite', 'review_date', 'created',)
