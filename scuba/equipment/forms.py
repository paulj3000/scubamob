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
        kwargs['commit'] = False
        obj = super(EquipmentForm, self).save(*args, **kwargs)
        obj.user = self.user
        obj.save()


class EquipmentMaintenanceForm(ModelForm):
    class Meta:
        model = EquipmentMaintenance
        fields = ['requireone', 'requiretwo', 'equipment']
