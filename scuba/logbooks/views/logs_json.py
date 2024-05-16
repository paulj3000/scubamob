from django.contrib.auth.decorators import login_required


@login_required
def logbookfolderlogs(us_request):
    raise NotImplementedError


@login_required
def logbookfolders(request):
    raise NotImplementedError
