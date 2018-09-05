from django.db import models
from django.contrib.auth.models import User
from utils.standards import TEMPERATURE
#from divespots.models import DiveSpot

class Temperature(models.Model):
    name            = models.CharField(max_length=20)
    
    class Meta:
        db_table    = 'scale_temperature'

class Length(models.Model):
    name            = models.CharField(max_length=20)
    
    class Meta:
        db_table    = 'scale_length'
