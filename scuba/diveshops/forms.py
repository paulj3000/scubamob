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

from utils.core.forms import NoSQLForm
from utils.external.google_address import GoogleAddress
from diveshops.mongo import DiveShop
from bson.objectid import ObjectId

class DiveShopForm(NoSQLForm):
    address = forms.CharField(max_length=20,label='Address')
    address2 = forms.CharField(max_length=20)
    city = forms.CharField(max_length=20,label='City')
    state = forms.CharField(max_length=20,label='State')
    zip = forms.CharField(max_length=20,label='Zip')

    def __init__(self, *args, **kwargs):
        self.site_id = kwargs.pop('site_id') if kwargs.keys().count('site_id') else None
        super(SiteForm, self).__init__(*args, **kwargs)

        self.Meta.id    = self.site_id
        if self.site_id:
            data = self.Object.collection.find_one({ '_id': ObjectId(self.site_id), 'user_id': self.user_id })
            if data:
                for field in self.fields.iterkeys():
                    self.fields[field].initial = data.get(field, "")
    class Meta:
        model = 'divesite'
        mongo   = DiveShop
        id      = 'site_id'

    def findsite(self, id):
        site = self.collection.find_one({'_id': ObjectId(id) })

        site['id']     = str(site['_id'])
        del(site['_id'])

        ## let's return our item
        return site

class DiveShopAddressForm(NoSQLForm):
    name = forms.CharField(max_length=200,label='Dive Shop Name')
    address = forms.CharField(max_length=200,label='Address')
    city = forms.CharField(max_length=200,label='City')
    state = forms.CharField(max_length=200,label='State')
    zip = forms.CharField(max_length=200,label='Zip Code')
    phone = forms.CharField(max_length=200,label='Phone')

    def save(self, *args, **kwargs):
        data    = self.cleaned_data

        gm  = GoogleAddress()
        latlng  = gm.get_data_city_state(self.cleaned_data['address'],
                            self.cleaned_data['city'],
                            self.cleaned_data['state'])


        data['latlng']    = { 'type': '2d', 'coordinates': [ latlng['longitude'], latlng['latitude'] ] }
        super(DiveShopAddressForm, self).save(data)

    class Meta:
        model = 'diveshops'
        mongo   = DiveShop

