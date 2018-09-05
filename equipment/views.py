from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login
from django.contrib import messages
from pprint import pprint
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.template import loader, Context
#from practiceapp.models import Practice
#from django.http import HttpResponse
from django.views.generic import CreateView
from django.shortcuts import render
#from django.http import HttpResponseRedirect
from django.views.generic  import CreateView, UpdateView
from django.http import HttpResponse, HttpResponseNotFound, Http404

from equipment.models import EquipmentMaintenance, Equipment
from equipment.forms import EquipmentForm
from equipment.forms import EquipmentMaintenanceForm

def index(us_request):
    equipment = Equipment.objects.all()
    t = loader.get_template("equipment/index.html")
    context = Context({ 'equipment': equipment })
    return HttpResponse(t.render(context))

def edit(request, equipment_id=None):
    context = {}
    if request.method == 'POST': # If the form has been submitted...
        if equipment_id:
            equipment_obj = get_object_or_404(Equipment, pk=equipment_id)

            ## let's verify the equipment matches the user
            if equipment_obj.user != request.user:
                raise Http404

            form = EquipmentForm(instance=equipment_obj, data=request.POST) # A form bound to the POST data
        else:
            form = EquipmentForm(request.POST) # A form bound to the POST data

        form.user    = request.user
        
        if form.is_valid(): # All validation rules pass
            new_addelement = form.save()
            return HttpResponseRedirect('/equipment/')

    elif equipment_id:
        equipment_obj = get_object_or_404(Equipment, pk=equipment_id)
        
        if equipment_obj.user != request.user:
            raise Http404
        form = EquipmentForm(instance=equipment_obj)
    else:
        form = EquipmentForm()

    return render(request, 'equipment/edit.html',  { 'form': form, 'equipment_id': equipment_id })


def delete_equipment(request, equipment_id):
    equipment_obj = get_object_or_404(Equipment, pk=equipment_id)

    if not equipment_obj or equipment_obj.user != request.user:
        raise Http404

    equipment_obj.delete()
    return HttpResponseRedirect('/equipment/')

def archive2(request):
    posts = Equipment.objects.all()
    t = loader.get_template("archive2.html")
    c = Context({ 'posts': posts })
    return HttpResponse(t.render(c))

def archive3(request):
    posts = EquipmentMaintenance.objects.all()
    t = loader.get_template("archive3.html")
    c = Context({ 'posts': posts })
    return HttpResponse(t.render(c))

def practice_requirements(request):
    if request.method == 'POST': # If the form has been submitted...
        print "in here"
        form = EquipmentMaintenanceForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            print "ATTEMPTING TO SAVE"
            new_requirements = form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = EquipmentMaintenanceForm()

    return render(request, 'add_requirement.html', { 'form': form})

def practice_require_edit(request, requirements_id):
    requirements1 = get_object_or_404(EquipmentMaintenance, pk=requirements_id)
    if request.method == 'POST': # If the form has been submitted...
        print "in here"
        form = EquipmentMaintenanceForm(instance=requirements1, data=request.POST)
        if form.is_valid(): # All validation rules pass
            print "ATTEMPTING TO SAVE"
            requirements1= form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = EquipmentMaintenanceForm(instance=requirements1)
    return render(request, 'add_requirement.html', { 'form': form})

def delete_requirement(request, requirements_id):
    deleterequire2 = get_object_or_404(EquipmentMaintenance, pk=requirements_id)
    if request.method == 'POST':
        print "in here"
        form = EquipmentMaintenanceForm(instance=deleterequire2, data=request.POST)
        if form.is_valid(): # All validation rules pass
            print "ATTEMPTING TO DELETE"
            deleterequire2.delete()
            return HttpResponseRedirect('/thanks/')
    else:
        form = EquipmentMaintenanceForm(instance=deleterequire2)
    return render(request, 'add_requirement.html', { 'form': form})



