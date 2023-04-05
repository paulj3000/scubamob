from pprint import pprint

from scuba.libs.nosql.mongo import Mongo
from bson.objectid import ObjectId

from django.db import models


class xDiveLog:
    COLLECTION = 'divelogs'

    def __init__(self):
        self._mongo = Mongo()
        self.collection = self._mongo[DiveLog.COLLECTION]

    def find(self, **kwargs):
        return self.collection.find(kwargs)

    def get_count(self, user_id):
        return self.collection.find({'user_id': user_id}).count()

    def get_divelog_subset(self, user_id, start, lim, sortBy):
        retval = []

        data = self.collection.find({'user_id': user_id}).skip(start).limit(lim)

        for log in data:
            retval.append(self.clean(log))

        return retval

    def get_log(self, **kwargs):
        if kwargs.get('id'):
            id = kwargs['id']
            del kwargs['id']
            kwargs['_id'] = ObjectId(id)

        return self.collection.find_one(kwargs)

    def clean(self, data):
        data['id'] = str(data['_id'])
        del data['_id']
        return data
