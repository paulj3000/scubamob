# -----------------------------------------------------------------------------
# libs/mail.py
#
# (C) Copyright 2015-2023, Pjs Midnight Labs.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
import time
import uuid

from django.utils.safestring import mark_safe
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from scuba.settings import EMAIL_FROM, EMAIL_BCC, BASE_URL, SITE_URL, TITLE_HTML

from scuba.libs.aws.s3 import S3
from scuba.settings import AWS_EMAIL_STORAGE_ROOT


def generate_email(user, template, context):
    ''' to be sent when a transaction was successful '''
    t = loader.get_template(template)

    # add some params to the user
    context.update({
        'user': user,
        'site_title': mark_safe(TITLE_HTML),
        'site_url': SITE_URL,
        'base_url': BASE_URL,
        'production_url': SITE_URL,
    })

    # now render the email and return
    return t.render(context)


def send_mail(user, subject, html_content, text_content=""):
    msg = EmailMultiAlternatives(subject, text_content, EMAIL_FROM, [user.email], bcc=[EMAIL_BCC])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    # store the email
    return store_email(user, html_content, subject)


def store_email(user, email, title):
    '''
    store the email in AWS so we have proof emails have gone
    out.
    '''
    s3 = S3(AWS_S3_BUCKET_PRIVATE)

    tstamp = int(time.time())
    upload_file = f"{AWS_EMAIL_STORAGE_ROOT}/accounts/{user.id}/{title}_{tstamp}.html"

    # generate the key name
    _ = s3.upload_data(upload_file, email, **{'ContentType': 'text/html'})

    # now return the uploaded file
    return upload_file


def generate_tracker():
    return str(uuid.uuid1())
