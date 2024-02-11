from django.contrib import admin

# Register your models here.
from scuba.security import models


admin.site.register(models.BlockedCountry)
admin.site.register(models.InvalidSignup)
