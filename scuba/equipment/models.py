from django.db import models
from scuba.accounts.models import User
from scuba.libs.models.uuidmodel import UUIDModel


class Equipment(UUIDModel):

    user = models.ForeignKey(User, related_name='equipment', on_delete=models.CASCADE)
    addone = models.CharField(max_length=200)
    addtwo = models.CharField(max_length=200)
    addthree = models.CharField(max_length=200)
    addfour = models.CharField(max_length=200)

    class Meta:
        db_table = 'equipment'


class EquipmentMaintenance(UUIDModel):
    equipment = models.ForeignKey(Equipment, related_name='maintenance', on_delete=models.CASCADE)
    requireone = models.CharField(max_length=200)
    requiretwo = models.CharField(max_length=200)

    class Meta:
        db_table = 'equipment_maintenance'
