import datetime

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from scuba.accounts.mongo import Account as AccountMongo


class MobileAppCredentials(models.Model):
    client_id   = models.CharField(max_length=64)
    phone_id    = models.CharField(max_length=64)
    secret_key  = models.CharField(max_length=128)
    active      = models.BooleanField(default=True)

    class Meta:
        db_table = 'mobile_app_credentials'

