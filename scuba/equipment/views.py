from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.http import HttpResponse

from scuba.equipment.models import EquipmentMaintenance, Equipment
from scuba.equipment.forms import EquipmentForm
from scuba.equipment.forms import EquipmentMaintenanceForm


@login_required
def index(request):
    equipment = Equipment.objects.filter(user=request.user)
    t = loader.get_template("equipment/index.html")
    return HttpResponse(t.render({'equipment': equipment}, request))


@login_required
def edit(request, equipment_id=None):
    if request.method == 'POST':
        if equipment_id:
            equipment_obj = get_object_or_404(Equipment, pk=equipment_id, user=request.user)
            form = EquipmentForm(instance=equipment_obj, data=request.POST)
        else:
            form = EquipmentForm(request.POST)

        form.user = request.user

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/equipment/')

    elif equipment_id:
        equipment_obj = get_object_or_404(Equipment, pk=equipment_id, user=request.user)
        form = EquipmentForm(instance=equipment_obj)
    else:
        form = EquipmentForm()

    return render(request, 'equipment/edit.html', {'form': form, 'equipment_id': equipment_id})


@login_required
def delete_equipment(request, equipment_id):
    equipment_obj = get_object_or_404(Equipment, pk=equipment_id, user=request.user)
    equipment_obj.delete()
    return HttpResponseRedirect('/equipment/')


@login_required
def archive2(request):
    posts = Equipment.objects.filter(user=request.user)
    t = loader.get_template("equipment/archive2.html")
    return HttpResponse(t.render({'posts': posts}, request))


@login_required
def archive3(request):
    posts = EquipmentMaintenance.objects.filter(equipment__user=request.user)
    t = loader.get_template("equipment/archive3.html")
    return HttpResponse(t.render({'posts': posts}, request))


@login_required
def practice_requirements(request):
    if request.method == 'POST':
        form = EquipmentMaintenanceForm(request.POST)
        form.fields['equipment'].queryset = Equipment.objects.filter(user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = EquipmentMaintenanceForm()
        form.fields['equipment'].queryset = Equipment.objects.filter(user=request.user)

    return render(request, 'equipment/add_requirement.html', {'form': form})


@login_required
def practice_require_edit(request, requirements_id):
    requirements1 = get_object_or_404(
        EquipmentMaintenance, pk=requirements_id, equipment__user=request.user)

    if request.method == 'POST':
        form = EquipmentMaintenanceForm(instance=requirements1, data=request.POST)
        form.fields['equipment'].queryset = Equipment.objects.filter(user=request.user)
        if form.is_valid():     # All validation rules pass
            requirements1 = form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = EquipmentMaintenanceForm(instance=requirements1)
        form.fields['equipment'].queryset = Equipment.objects.filter(user=request.user)
    return render(request, 'equipment/add_requirement.html', {'form': form})


@login_required
def delete_requirement(request, requirements_id):
    deleterequire2 = get_object_or_404(
        EquipmentMaintenance, pk=requirements_id, equipment__user=request.user)

    if request.method == 'POST':
        form = EquipmentMaintenanceForm(instance=deleterequire2, data=request.POST)
        form.fields['equipment'].queryset = Equipment.objects.filter(user=request.user)
        if form.is_valid():
            deleterequire2.delete()
            return HttpResponseRedirect('/thanks/')
    else:
        form = EquipmentMaintenanceForm(instance=deleterequire2)
        form.fields['equipment'].queryset = Equipment.objects.filter(user=request.user)
    return render(request, 'equipment/add_requirement.html', {'form': form})
