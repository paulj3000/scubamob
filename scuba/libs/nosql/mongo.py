# -*- coding: utf-8 -*-

from pymongo import MongoClient
from django.conf import settings


def Mongo(connection_params=settings.MONGO):
    try:
        if connection_params['USE_REPLICASET']:
            mongo_conn = MongoClient(connection_params['HOSTS'],
                connection_params['PORT'],
                replicaSet=connection_params['REPLICASET'])
        else:
            mongo_conn = MongoClient(host=connection_params['HOST'], port=connection_params['PORT'])
        conn = mongo_conn[connection_params['DATABASE']]
        if connection_params.get('USERNAME') and connection_params.get('PASSWORD'):
            conn.authenticate(connection_params['USERNAME'], connection_params['PASSWORD'])
        return conn

    except (Exception, ConnectionError):
        raise
    #Log().exception(ConnectionError)
        raise ConnectionError
