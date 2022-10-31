from __future__ import division
from django.conf import settings

from scuba.libs.nosql.mongo import Mongo
from bson.objectid import ObjectId

class DiveShop:
    COLLECTION   = 'diveshops'

    def __init__(self):
        self._mongo = Mongo()
        self.collection    = self._mongo[DiveShop.COLLECTION]

    def get_all_sites(self):
        retval  = []

        for sites in self.collection.find():
            retval.append(sites)

        return retval

    def get_diveshop_info(self, diveshopid):
        return self.collection.find_one({ '_id': ObjectId(diveshopid) })

    def get_local_diveshops(self, lon, lat, radius):
        radius = radius / settings.EARTH_RADIUS
        retval  = []
        shops = self.collection.find({ "latlng.coordinates": { '$geoWithin': { '$centerSphere': [[ lon, lat ], radius ] }}})

        for shop in shops:
            coords  = shop['latlng']['coordinates']
            del(shop['latlng']['coordinates'])
            del(shop['latlng']['type'])
            shop['latlng']['latitude']    = coords[1]
            shop['latlng']['longitude']    = coords[0]

            retval.append(self.clean(shop))

        return retval

    def clean(self, data):
        data['id']  = str(data['_id'])
        del data['_id']
        return data
