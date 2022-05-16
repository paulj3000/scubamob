import uuid
from bson.objectid import ObjectId

from django import forms
from pprint import pprint

from utils.nosql.mongo import Mongo

from scuba.settings import NOSQL_HOST, NOSQL_PORT, NOSQL_DB

class NoSQLForm(forms.Form):
    # construct a new UUID field based on a UUID
    def __init__(self, *args, **kwargs):
        self.db = Mongo()
        self.collection = self.db[self.Meta.model]
        self.Object  = self.Meta.mongo()

        self.user_id = kwargs.pop('user_id') if 'user_id' in kwargs.keys() else None
        super(NoSQLForm, self).__init__(*args, **kwargs)

    def save(self, data = None):
        if not data:
            data   = self.cleaned_data

        if hasattr(self.Meta, 'id') and self.Meta.id:
            # let's perform our update
            self.collection.update({ '_id': self.Meta.id }, { "$set": data })
        else:
            print("starting the save process here 1234")
            guid    =   str(uuid.uuid1()).replace('-','')
            # nope, let's add our new document
            data.update({ '_id': { 'user': self.user_id, 'guid': guid }, 'user_id': self.user_id })
            self.collection.insert(data)
