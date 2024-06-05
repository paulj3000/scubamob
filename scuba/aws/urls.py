from django.urls import path

import scuba.aws.apis as aws_apis


urlpatterns = [
    path('cicd/build', aws_apis.CodeBuildAPI.as_view()),
    path('cicd/pipeline', aws_apis.CodePipelineAPI.as_view()),
]
