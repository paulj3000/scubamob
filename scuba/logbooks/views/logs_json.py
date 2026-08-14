import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from scuba.logbooks.models import LogbookFolder


def _folder_to_dict(folder):
    return {'id': folder.pk_as_str, 'name': folder.name}


@login_required
def logbookfolders(request):
    if request.method == 'POST':
        body = json.loads(request.body or '{}')
        foldername = body.get('foldername')
        if foldername:
            LogbookFolder.objects.get_or_create(user=request.user, name=foldername)

    folders = LogbookFolder.objects.filter(user=request.user)
    return JsonResponse({'folders': [_folder_to_dict(folder) for folder in folders]})


@login_required
def logbookfolderlogs(request):
    folder_id = request.GET.get('id')
    folder = get_object_or_404(LogbookFolder, pk=folder_id, user=request.user)

    # LogbookFolder has no relationship to Logbook in the current schema, so
    # there is nothing real to scope "this folder's logs" to yet.
    return JsonResponse({'id': folder.pk_as_str, 'name': folder.name, 'logs': []})
