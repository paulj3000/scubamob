from scuba.libs.nosql.mongo import Mongo
from bson.objectid import ObjectId

class DiveSite:
    COLLECTION   = 'divesites'

    def __init__(self):
        self._mongo = Mongo()
        self.collection    = self._mongo[DiveSite.COLLECTION]

    def get_all_sites(self):
        retval  = []

        for sites in self.collection.find():
            retval.append(sites)

        return retval

    def get_divesite_info(self, divesiteid):
        return self.collection.find_one({ '_id': ObjectId(divesiteid) })
