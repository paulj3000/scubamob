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
from pprint import pprint

from django import forms

from utils.core.forms import NoSQLForm
from scuba.divesites.mongo import DiveSite
from bson.objectid import ObjectId

CLASSIFICATION_CHOICES = (('shark', 'Shark'),('reef', 'Reef'), ('wall', 'Wall'),
                            ('wreck', 'Wreck'),('drift', 'Drift'),('dropoff', 'Drop Off'),
                            ('muck', 'Muck'),('cave', 'Cave'),('ice', 'Ice'),('night', 'Night'),
                            ('rock', 'Rock'),('deep', 'Deep'),('inland', 'Inland'),('other', 'Other'))

class SiteForm(NoSQLForm):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'inputbox2'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea'}), required=False)
    address = forms.CharField(max_length=80,label='Address', widget=forms.TextInput(attrs={'class':'inputbox2'}))
    address2 = forms.CharField(max_length=80, required=False, widget=forms.TextInput(attrs={'class':'inputbox2'}))
    city = forms.CharField(max_length=20,label='City', widget=forms.TextInput(attrs={'class':'inputbox2'}))
    state = forms.CharField(max_length=20,label='State', widget=forms.TextInput(attrs={'class':'inputbox2'}))
    zip = forms.CharField(max_length=20,label='Zip', widget=forms.TextInput(attrs={'class':'inputbox2'}))
    latitude = forms.CharField(max_length=20,label='Latitude', widget=forms.TextInput(attrs={'class':'inputbox2'}))
    longitude = forms.CharField(max_length=20,label='Longitude', widget=forms.TextInput(attrs={'class':'inputbox2'}))
    classifications = forms.MultipleChoiceField(label='Classification', required=False,
			widget=forms.SelectMultiple(attrs={'autocomplete':'off', 'class':'inputbox2 chosen-select', \
			'data-placeholder': "Choose Classifications"}),
			choices=CLASSIFICATION_CHOICES)

    def __init__(self, *args, **kwargs):
        self.site_id = kwargs.pop('site_id') if 'site_id' in kwargs.keys() else None
        self.save_address = True

        super().__init__(*args, **kwargs)

        self.Meta.id = self.site_id
        if self.site_id:
            #data = self.Object.collection.find_one({ '_id': ObjectId(self.site_id), 'user_id': self.user_id })
            data = self.Object.collection.find_one({ '_id': ObjectId(self.site_id) })
            pprint(data)
            if data:
                # first, let's normalize the data...
                for k, v in data['address'].iteritems():
                    data[k] = v

                for k, v in data['latlng'].iteritems():
                    data[k] = v

                for field in self.fields.iterkeys():
                    self.fields[field].initial = data.get(field, "")

    # before we save the form, let's format the data so it's in an appropriate manner
    def save(self):
        data = self.cleaned_data

        new_data = { 'title': data['title'], 'description': data['description'], 'user_id': self.user_id }

        if self.save_address:
            new_data['address'] = {
                        'address': data.get('address'),
                        'address2': data.get('address2'),
                        'city': data.get('city'),
                        'state': data.get('state'),
                        'zip': data.get('zip'),
                    }

        new_data['latlng'] = {
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                }

        # save the form
        super().save(new_data)

    def clean_latitude(self):
        data = self.cleaned_data['latitude']
        error_str = 'Please enter a valid latitude'

        try:
            data = float(data)
            if data < -90.0 or data > 90.0:
                raise forms.ValidationError(error_str)
        except:
            raise forms.ValidationError(error_str)

        return data

    def clean_longitude(self):
        data = self.cleaned_data['longitude']
        error_str = 'Please enter a valid longitude'

        try:
            data = float(data)
            if data < -180. or data > 180.0:
                raise forms.ValidationError(error_str)
        except:
            raise forms.ValidationError(error_str)

        return data

    # let's do some cleaning of the form....
    def clean(self):
        cleaned_data = super().clean()

        to_del = ['address', 'city', 'state', 'zip']
        if cleaned_data.get('latitude') and cleaned_data.get('longitude'):
            # excellent, we do not need the address since we already have the
            # latitude / longitude
            for d in to_del:
                if self._errors.get(d):
                    self.save_address = False
                    del(self._errors[d])

        # finally, do we want to save an address?

        return cleaned_data

    class Meta:
        model = 'divesites'
        mongo = DiveSite
        id = 'site_id'

    def findsite(self, id):
        site = self.collection.find_one({'_id': ObjectId(id) })

        site['id'] = str(site['_id'])
        del(site['_id'])

        # let's return our item
        return site
