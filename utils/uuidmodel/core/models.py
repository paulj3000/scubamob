from django_extensions.db.fields import UUIDField
from django.contrib.auth.admin import UserAdmin

def replace_primary_key(model):
    # remove the original id field
    model._meta.local_fields = filter(lambda u: u.name is not 'id', model._meta.local_fields)
    
    # clear the pk and auto_field meta properties
    model._meta.pk = None
    model._meta.has_auto_field = False
    model._meta.auto_field = None

    # add a new UUID field as the primary key
    model.add_to_class('id', UUIDField(primary_key=True))
    
    # finally, move the new UUID field back to the first position in the field list.
    # this is necessary as the admin module creates LogEntry objects with an assumed field ordering.
    model._meta.local_fields.insert(0, model._meta.local_fields.pop())


# site models
from django.contrib.sites import models as sites_models
replace_primary_key(sites_models.Site)

# content-type models
from django.contrib.contenttypes import models as contenttypes_models
replace_primary_key(contenttypes_models.ContentType)

# admin models
from django.contrib.admin import models as admin_models
replace_primary_key(admin_models.LogEntry)

# auth (user, group, permission, etc) models
from django.contrib.auth import models as auth_models
replace_primary_key(auth_models.User)
replace_primary_key(auth_models.Permission)
replace_primary_key(auth_models.Group)
replace_primary_key(auth_models.Message)

# fix up the join tables, as well.
[replace_primary_key(join.rel.through) for join in auth_models.User._meta.many_to_many]
[replace_primary_key(join.rel.through) for join in auth_models.Group._meta.many_to_many]

# fix the auth/admin's get_urls function:
### TODO: this is still being overriden by the original version. 
###       Prevents password from being changed in the admin interface.
###       investigate! 
def get_urls_with_uuids(self):
    from django.conf.urls.defaults import patterns
    return patterns('',
        (r'^(\d+)/password/$', self.admin_site.admin_view(self.user_change_password))
        (r'^([0-9a-f\-]{36})/password/$', self.admin_site.admin_view(self.user_change_password)),
    ) + super(UserAdmin, self).get_urls()

from django.contrib.auth import admin
admin.get_urls = get_urls_with_uuids

