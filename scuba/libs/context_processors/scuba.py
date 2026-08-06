"""
skm/libs/context_processors/skm.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Our context preprocessor. Add some extra stuff to the context
before we print out our page
"""
import os

from django.conf import settings
from scuba.sitesettings.models import SystemSetting


def Scuba(request):
    '''
    populate the header and footer fields of the template
    '''
    user = request.user

    context = {
        'site_title': settings.SITE_TITLE,
        'html_name': settings.TITLE_HTML,
        'is_production': settings.IS_PRODUCTION or os.environ.get('IS_BUILDING'),
        'chat_server_active': SystemSetting.get_chat_server_active(),
        'alert_server_active': SystemSetting.get_alert_server_active()
    }

    # if the user is logged in, get his profile image
    if user.is_authenticated:
        context['profile_image'] = request.session.get('profile_image', user.get_profile_image())

    # surface an always-visible banner while an admin is impersonating this user
    context['impersonating'] = bool(request.session.get('impersonator_id'))

    # set up the main menu

    return context
