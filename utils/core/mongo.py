from pprint import pprint

from utils.nosql.mongo import Mongo as MongoDB
from bson.objectid import ObjectId

class Mongo:
    def __init__(self):
        assert self.Meta.collection 
        
        self._mongo = MongoDB()
        self.collection    = self._mongo[self.Meta.collection]

    def get_count(self, user_id):
        return self.collection.find( { 'user_id': user_id }).count()

    def get_divelog_subset(self, user_id, start, lim, sortBy):
        retval  = []

        data =  self.collection.find({ 'user_id': user_id }).skip(start).limit(lim)

        for log in data:
            retval.append(self.clean(log))
        
        return retval

    def clean(self, data):
        data['id']  = str(data['_id'])
        del data['_id']
        return data

