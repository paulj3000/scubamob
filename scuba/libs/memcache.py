from datetime import datetime, timedelta
from decimal import Decimal
from pprint import pprint
import logging
import memcache

from django.conf import settings

class MemcacheClient:
    def __init__(self, namespace):
        self.namespace = namespace
        self.settings = settings.MEMCACHE
        self.memcache_obj = memcache.Client(self.settings['server'])

        if not len(self.memcache_obj.get_stats()):
            raise ConnectionError("memcache not available");

    def set(self, key, value, timeout=0):
        key = "%s%s" % (self.namespace, key)
        key = key.encode()

        self.memcache_obj.set(key, value, timeout)

    def get(self, key):
        key = "%s%s" % (self.namespace, key)
        key = key.encode()

        return self.memcache_obj.get(key)
