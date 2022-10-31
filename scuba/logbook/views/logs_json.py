import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core import serializers

from scuba.logbook.forms import DiveForm
from scuba.logbook.models import LogbookFolder
from scuba.logbook.mongo import DiveLog


@login_required
def logbookfolderlogs(us_request):
    # first, let's get the user from the object
    user = us_request.user

    # get the id from the query string, the one we're querying against...
    id = us_request.GET.get('id')

    # ...and finally, query against it.  We only want to see anything w/ this
    # id and this user
    response = {}
    try:
        folder = user.logbook_folders.get(id=id)

        divelog_mongo = DiveLog()
        logs = divelog_mongo.collection.find({ '_id.user': user.id }, { '_id': 1, 'name': 1 })

        response = { 'name': folder.name, 'logs': list(logs) }

    except:
        raise

    return JSONResponse(response)


@login_required
def logbookfolders(request):
    user = request.user

    id = request.GET.get('id')
    divelog_mongo = DiveLog()
    if request.is_ajax():
        form_data = None
        folder = None
        if request.method == 'POST':
            try:
                form_data = json.loads(request.body)
            except:
                error = 'Invalid Data'

            if form_data:
                try:
                    folder = LogbookFolder.objects.create(user=user, name=form_data.get('foldername'))
                except:
                    error = 'Duplicate Folder Name'

    folders = user.logbook_folders.values('id', 'name').order_by('name').all()

    to_search = { '_id.user': user.id }
    if id:
        to_search['meta.folder'] = id
    else:
        to_search['meta.folder'] = {'$exists': False }

    logs = []

    for x in divelog_mongo.collection.find(to_search):
        logs.append({ 'id': x['_id']['id'], 'title': x['title'], 'date': x['date'] })

    return JSONResponse({ 'folders': list(folders), 'logs': logs })
