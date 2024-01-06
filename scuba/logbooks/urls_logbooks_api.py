from django.urls import path

import scuba.logbooks.apis.logbook as logbook_api


urlpatterns = [
    path('', logbook_api.GetAllLogbooks.as_view()),
]
