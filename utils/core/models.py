from django.db import models
from django.db.models import DateTimeField
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
import datetime

def utctime_save(self, model, add):
    value = datetime.datetime.utcnow()
    setattr(model,self.attname,value)
    return value

def utc__init__(self, *args, **kwargs):
    kwargs.setdefault('editable', False)
    kwargs.setdefault('blank', True)
    kwargs.setdefault('default', datetime.datetime.utcnow)
    DateTimeField.__init__(self, *args, **kwargs)

ModificationDateTimeField.pre_save = utctime_save
CreationDateTimeField.__init__ = utc__init__

class Created(models.Model):
    created = CreationDateTimeField()
    class Meta:
        abstract = True

class Modified(models.Model):
    modified = ModificationDateTimeField()
    class Meta:
        abstract = True

class Timestamped(Created, Modified):
    class Meta:
        abstract = True

# add an efficient, non-throwing 'first' retrieval function to QuerySet
def first(self):
    result = list(self[:1])
    if result:
        return result[0]
    return None

from django.db import models
# http://www.djangosnippets.org/snippets/562/#c673
class QuerySetManager(models.Manager):
    # http://docs.djangoproject.com/en/dev/topics/db/managers/#using-managers-for-related-object-access
    # Not working cause of:
    # http://code.djangoproject.com/ticket/9643
    use_for_related_fields = True
    def __init__(self, qs_class=models.query.QuerySet):
        self.queryset_class = qs_class
        super(QuerySetManager, self).__init__()

    def get_query_set(self):
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

from django.db.models.query import QuerySet
QuerySet.first = first

class QuerySet(models.query.QuerySet):
    @classmethod
    def as_manager(cls, ManagerClass=QuerySetManager):
        return ManagerClass(cls)
