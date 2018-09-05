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
from pprint import pprint

from django import forms

from utils.core.forms import NoSQLForm
from logbook.mongo import DiveLog

VISIBILITY_CHOICES = (('bad', 'Bad'),('average', 'Average'),('good', 'Good'),('excellent', 'Excellent'))
TANK_CHOICES = (('steel', 'Steel'),('carbon', 'Carbon'),('aluminium', 'Aluminium'))

class DiveForm(NoSQLForm):
    dive_id = forms.IntegerField(label='Dive Number?')
    date = forms.CharField(max_length=20)
    title = forms.CharField(max_length=20,label='Title')
    timeIn = forms.CharField(max_length=20,label='Time in')
    timeOut = forms.CharField(max_length=20,label='Time out')
    maxDepth = forms.CharField(max_length=20,label='Max depth')
    airTemp = forms.CharField(max_length=20,label='Air temperature')
    waterTemp = forms.CharField(max_length=20,label='Water temperature')
    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
    buddy = forms.CharField(max_length=20,label='Buddy')
    tank = forms.ChoiceField(choices=TANK_CHOICES)
    tankSize = forms.CharField(max_length=20,label='Tank size')
    tankAir = forms.CharField(max_length=20,label='Tank air')
    startPressure = forms.CharField(max_length=20,label='Start Pressure')
    endPressure = forms.CharField(max_length=20,label='End Pressure')
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        self.log_id = kwargs.pop('log_id') if kwargs.keys().count('log_id') else None
        super(DiveForm, self).__init__(*args, **kwargs)
        last_item   = self.collection.find({ "user_id": self.user_id }).sort("dive_id", -1).limit(1)
        initial = 1
        if last_item.count():
            data    = last_item.next()
            if data.get('dive_id'):
                initial = data.get('dive_id') +1

        self.Meta.id    = self.log_id
        if self.log_id: 
            _id = { guid: self.log_id, user_id: self.user_id }
            data = self.Object.collection.find_one({ '_id': _id, 'user_id': self.user_id })
            if data:
                for field in self.fields.iterkeys():
                    self.fields[field].initial = data.get(field, "")
        else:
            ### just initialize the form data
            self.fields['dive_id'].initial = initial
    class Meta:
        model = 'divelogs'
        mongo   = DiveLog
        id      = 'log_id'

    def findlog(self, id):
        divelog = self.collection.find_one({'_id': id })       

        divelog['id']     = divelog['_id']['guid']
        del(divelog['_id'])

        ## let's return our item
        return divelog
    
    def save(self):
        cleaned = self.cleaned_data

        data   = { 'data': cleaned, 'title': cleaned['title'], 'date': cleaned['date'] }
        super(DiveForm, self).save(data)
