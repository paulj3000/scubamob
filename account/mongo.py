from pprint import pprint

from utils.nosql.mongo import Mongo
from bson.objectid import ObjectId

class Account:
    class Meta:
        collection  = 'accounts'

    def __init__(self, **kwargs):
        self._mongo = Mongo()
        self.user_id        = kwargs.get('user_id')
        self.collection     = self._mongo[self.Meta.collection]
        
        ## let's make sure mongo has this account's record in its collection
        if not self.collection.find({ '_id': self.user_id }).count():
            ## let's create the new record
            self.collection.insert({ '_id': self.user_id })

        self.account    = self.collection.find({ '_id': self.user_id })
    
    def get_favorites(self):
        ''' get all the favorites'''
        return self.account[0].get('favorites', [])

    def set_favorite(self, divesiteid, method):
        ''' set / unset the divesiteid into the favorites function '''
        method = '$addToSet' if method == 'true' else '$pull'
        self.collection.update( { '_id': self.user_id }, { method: { 'favorites': divesiteid }})
    
    def is_favorite(self, divesiteid):
        ''' set / unset the divesiteid into the favorites function '''
        return True if self.collection.find({ '_id': self.user_id, 'favorites': { '$in': [divesiteid] }}).count() else False

    
    def clean(self, data):
        data['id']  = str(data['_id'])
        del data['_id']
        return data

