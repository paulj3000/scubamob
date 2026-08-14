from django.forms import ModelForm

from scuba.equipment.models import Equipment
from scuba.equipment.models import EquipmentMaintenance


class EquipmentForm(ModelForm):
    class Meta:
        model = Equipment
        fields = ['addone', 'addtwo', 'addthree', 'addfour']

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        obj = super(EquipmentForm, self).save(*args, **kwargs)
        obj.user = self.user
        obj.save()
        return obj


class EquipmentMaintenanceForm(ModelForm):
    class Meta:
        model = EquipmentMaintenance
        fields = ['requireone', 'requiretwo', 'equipment']
