from utils.nosql.mongo import Mongo
from bson.objectid import ObjectId

class Equipment:
    COLLECTION   = 'equipment'

    def __init__(self):
        self._mongo = Mongo()
        self.collection    = self._mongo[Equipment.COLLECTION]

    def get_count(self, user_id):
        return self.collection.find( { 'user_id': user_id }).count()

    ### this is just a function for you to review.....it does not need to be implemented
    def get_equipment_subset(self, user_id, start, lim, sortBy):
        retval  = []

        data =  self.collection.find({ 'user_id': user_id }).skip(start).limit(lim)

        for log in data:
            retval.append(self.clean(log))

        return retval

    def clean(self, data):
        data['id']  = str(data['_id'])
        del data['_id']
        return data
