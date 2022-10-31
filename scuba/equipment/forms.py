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
from django.forms import ModelForm

from scuba.equipment.models import Equipment
from scuba.equipment.models import EquipmentMaintenance


class EquipmentForm(ModelForm):
    class Meta:
        model = Equipment
        fields = ['addone', 'addtwo', 'addthree', 'addfour']

    def save(self, *args, **kwargs):
        kwargs['commit']=False
        obj = super(EquipmentForm, self).save(*args, **kwargs)
        obj.user = self.user
        obj.save()



class EquipmentMaintenanceForm(ModelForm):
    class Meta:
        model = EquipmentMaintenance
        fields = ['requireone', 'requiretwo', 'equipment']




#from pprint import pprint

#from django import forms

#from utils.core.forms import NoSQLForm
#from equipment.mongo import Equipment
#from bson.objectid import ObjectId

#VISIBILITY_CHOICES = (('bad', 'Bad'),('average', 'Average'),('good', 'Good'),('excellent', 'Excellent'))
#TANK_CHOICES = (('steel', 'Steel'),('carbon', 'Carbon'),('aluminium', 'Aluminium'))

#class EquipmentForm(NoSQLForm):
    ### add variables here
#    dive_id = forms.IntegerField(label='Dive Number?')
#    date = forms.CharField(max_length=20)
#    title = forms.CharField(max_length=20,label='Title')
#    timeIn = forms.CharField(max_length=20,label='Time in')
#    timeOut = forms.CharField(max_length=20,label='Time out')
#    maxDepth = forms.CharField(max_length=20,label='Max depth')
#    airTemp = forms.CharField(max_length=20,label='Air temperature')
#    waterTemp = forms.CharField(max_length=20,label='Water temperature')
#    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
#    buddy = forms.CharField(max_length=20,label='Buddy')
#    tank = forms.ChoiceField(choices=TANK_CHOICES)
#    tankSize = forms.CharField(max_length=20,label='Tank size')
#    tankAir = forms.CharField(max_length=20,label='Tank air')
#    startPressure = forms.CharField(max_length=20,label='Start Pressure')
#    endPressure = forms.CharField(max_length=20,label='End Pressure')
#    notes = forms.CharField(widget=forms.Textarea, required=False)

#    def __init__(self, *args, **kwargs):
#        self.equipment_id = kwargs.pop('equipment_id') if kwargs.keys().count('equipment_id') else None
#        super(DiveForm, self).__init__(*args, **kwargs)
#        last_item   = self.collection.find({ "user_id": self.user_id }).sort("dive_id", -1).limit(1)
#        initial = 1
#        if last_item.count():
#            data    = last_item.next()
#            initial = data['dive_id']+1
#
#        self.Meta.id    = self.equipment_id
#        if self.equipment_id:
#            data = self.Object.collection.find_one({ '_id': ObjectId(self.equipment_id), 'user_id': self.user_id })
#            if data:
#                for field in self.fields.iterkeys():
#                    self.fields[field].initial = data.get(field, "")
#        else:
#            ### just initialize the form data
#            self.fields['dive_id'].initial = initial
#    class Meta:
#        model = 'equipment'
#        mongo   = Equipment
#        id      = 'equipment_id'
#
#    def findlog(self, id):
#        divelog = self.collection.find_one({'_id': ObjectId(id) })
#
#        divelog['id']     = str(divelog['_id'])
#        del(divelog['_id'])
#
#        ## let's return our item
#        return divelog
