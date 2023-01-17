from django.urls import path, re_path
from django.views.generic import TemplateView

import scuba.logbooks.apis.logbook as logbook_api


urlpatterns = [
    path('', logbook_api.GetAllLogbooks.as_view()),
]
