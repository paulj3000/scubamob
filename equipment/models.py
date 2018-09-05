from django.db import models
from django.contrib.auth.models import User

class Equipment(models.Model):
    
    user = models.ForeignKey(User, related_name='equipment' )
    addone = models.CharField(max_length=200)
    addtwo = models.CharField(max_length=200)
    addthree = models.CharField(max_length=200)
    addfour = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'equipment'

class EquipmentMaintenance(models.Model):
    equipment = models.ForeignKey(Equipment, related_name='maintenance' )
    requireone = models.CharField(max_length=200)
    requiretwo = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'equipment_maintenance'

