from django.contrib import admin

# Register your models here.
from scuba.security.models import BlockedCountry


admin.site.register(BlockedCountry)
