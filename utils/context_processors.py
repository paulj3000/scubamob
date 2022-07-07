from django.conf import settings

from scuba.settings import SOCIAL_MEDIA


def sm(request):
    """
    populate the header and footer fields of the template
    """
    user = request.user

    context = {
            'logged_in': user.is_authenticated,
            'social_media': SOCIAL_MEDIA,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'SITE_NAME': settings.SITE_NAME
            }

    if user.is_authenticated:
        context.update({'fullname': user.get_full_name(), 'email': user.email})

    return context
