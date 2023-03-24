"""
skm/libs/context_processors/skm.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Our context preprocessor. Add some extra stuff to the context
before we print out our page
"""
from django.conf import settings


def Scuba(request):
    '''
    populate the header and footer fields of the template
    '''
    user = request.user

    context = {
        'site_title': settings.SITE_TITLE,
        'html_name': settings.TITLE_HTML,
        'is_production': settings.IS_PRODUCTION,
    }

    # if the user is logged in, get his profile image
    if user.is_authenticated:
        context['profile_image'] = request.session.get('profile_image', user.get_profile_image())

    # set up the main menu

    return context
