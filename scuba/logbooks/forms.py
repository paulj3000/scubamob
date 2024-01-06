# -----------------------------------------------------------------------------
# scuba/logbook/forms.py
#
# This is the main class for the migrator.  This will take in a username, and
# an optional new username.  The result will dictate whether the account can
# successfully be migrated
#
# (C) Copyright 2013, Divespot.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from django import forms


TANK_CHOICES = (('steel', 'Steel'), ('carbon', 'Carbon'), ('aluminium', 'Aluminium'))
VISIBILITY_CHOICES = (
    ('bad', 'Bad'), ('average', 'Average'), ('good', 'Good'),
    ('excellent', 'Excellent'))


class DiveForm(forms.Form):
    dive_id = forms.IntegerField(label='Dive Number?')
    date = forms.CharField(max_length=20)
    title = forms.CharField(max_length=20, label='Title')
    timeIn = forms.CharField(max_length=20, label='Time in')
    timeOut = forms.CharField(max_length=20, label='Time out')
    maxDepth = forms.CharField(max_length=20, label='Max depth')
    airTemp = forms.CharField(max_length=20, label='Air temperature')
    waterTemp = forms.CharField(max_length=20, label='Water temperature')
    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
    buddy = forms.CharField(max_length=20, label='Buddy')
    tank = forms.ChoiceField(choices=TANK_CHOICES)
    tankSize = forms.CharField(max_length=20, label='Tank size')
    tankAir = forms.CharField(max_length=20, label='Tank air')
    startPressure = forms.CharField(max_length=20, label='Start Pressure')
    endPressure = forms.CharField(max_length=20, label='End Pressure')
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = 'divelogs'
        id = 'log_id'

    def findlog(self, id):
        divelog = self.collection.find_one({'_id': id})

        divelog['id'] = divelog['_id']['guid']
        del (divelog['_id'])

        # let's return our item
        return divelog

    def save(self):
        cleaned = self.cleaned_data

        data = {'data': cleaned, 'title': cleaned['title'], 'date': cleaned['date']}
        super().save(data)
