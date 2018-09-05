from django.conf.urls import patterns, include, url
#from practiceapp.models import Practice
from equipment import views
from equipment.models import Equipment
#from practicesearch.models import Practice2
#from practicesearch import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.index, name="equipment_home"),
    url(r'edit/(?P<equipment_id>[0-9]+)/?$', views.edit, name='equipment_edit_id'),
    url(r'edit/', views.edit, name="equipment_edit"),
    url(r'delete/(?P<equipment_id>[0-9]+)/?$', views.delete_equipment, name='equipment_delete'),

    url(r'^practiceapp2/', views.archive2),
    url(r'^requirementsview/', views.archive3),
    url(r'^practicerequire/', views.practice_requirements),
    url(r'^(?P<requirements_id>\d+)/practicerequire_edit/$', views.practice_require_edit, name='practice_require_edit'),
    url(r'^(?P<requirements_id>\d+)/requirements_delete/$', views.delete_requirement, name='delete_requirement'),
)
