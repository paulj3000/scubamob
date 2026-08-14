from django.urls import path

import scuba.diveshops.views as diveshops_views


urlpatterns = [
    path('', diveshops_views.index, name="diveshops_home"),
    path('json/getlocaldiveshops/', diveshops_views.getlocaldiveshops),
]
