from django.urls import path, re_path

from scuba.equipment import views


urlpatterns = [
    # Examples:
    path(r'', views.index, name="equipment_home"),
    re_path(r'edit/(?P<equipment_id>[0-9]+)/?$',
            views.edit,
            name='equipment_edit_id'),
    path(r'edit/',
         views.edit,
         name="equipment_edit"),
    re_path(r'delete/(?P<equipment_id>[0-9]+)/?$',
            views.delete_equipment,
            name='equipment_delete'),

    path('practiceapp2/', views.archive2),
    path('requirementsview/', views.archive3),
    path('practicerequire/', views.practice_requirements),
    re_path(r'^(?P<requirements_id>\d+)/practicerequire_edit/$',
            views.practice_require_edit,
            name='practice_require_edit'),

    re_path(r'^(?P<requirements_id>\d+)/requirements_delete/$',
            views.delete_requirement,
            name='delete_requirement'),
]
