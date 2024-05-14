from django.urls import path

import scuba.system.apis as system_apis


urlpatterns = [
    path('cicd/build', system_apis.CodeBuildAPI.as_view()),
    path('cicd/pipeline', system_apis.CodePipelineAPI.as_view()),
]
