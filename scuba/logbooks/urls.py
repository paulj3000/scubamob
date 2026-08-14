from django.urls import path

import scuba.logbooks.views.dives as dives_views
import scuba.logbooks.views.logs_json as logs_json


urlpatterns = [
    path('', dives_views.index, name="logbook_home"),

    path('json/logbookfolders', logs_json.logbookfolders),
    path('json/logbookfolderlogs', logs_json.logbookfolderlogs),
]
