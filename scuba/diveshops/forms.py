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

from utils.external.google_address import GoogleAddress


class DiveShopForm(forms.Form):
    address = forms.CharField(max_length=20, label='Address')
    address2 = forms.CharField(max_length=20)
    city = forms.CharField(max_length=20, label='City')
    state = forms.CharField(max_length=20, label='State')
    zip = forms.CharField(max_length=20, label='Zip')

    def __init__(self, *args, **kwargs):
        self.site_id = kwargs.pop('site_id') if kwargs.keys().count('site_id') else None
        super().__init__(*args, **kwargs)

    class Meta:
        model = 'divesite'


class DiveShopAddressForm(forms.ModelForm):
    name = forms.CharField(max_length=200, label='Dive Shop Name')
    address = forms.CharField(max_length=200, label='Address')
    city = forms.CharField(max_length=200, label='City')
    state = forms.CharField(max_length=200, label='State')
    zip = forms.CharField(max_length=200, label='Zip Code')
    phone = forms.CharField(max_length=200, label='Phone')

    def save(self, *args, **kwargs):
        data = self.cleaned_data

        gm = GoogleAddress()
        latlng = gm.get_data_city_state(
            self.cleaned_data['address'],
            self.cleaned_data['city'],
            self.cleaned_data['state'])

        data['latlng'] = {
            'type': '2d',
            'coordinates': [latlng['longitude'], latlng['latitude']]}
        super().save(data)

    class Meta:
        model = 'diveshops'
