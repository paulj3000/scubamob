from django.conf import settings

def sm(request):
    """ 
    populate the header and footer fields of the template
    """ 
    user    = request.user

    context = { 
            'logged_in': user.is_authenticated(),
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'IMAGE_URL': settings.DEV_MEDIA_URL if settings.DEBUG else settings.PRODUCTION_MEDIA_URL,
            'PRODUCTION_GALLERY_URL': settings.PRODUCTION_GALLERY_URL
            }

    if user.is_authenticated():
        context.update({ 'fullname': user.get_full_name(), 'email': user.email, 'username': user.username })

    return context
