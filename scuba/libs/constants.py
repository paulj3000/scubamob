"""
skm/skmbilling/constants.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Define some constants for the billing module
"""
from __future__ import unicode_literals

SUBSCRIPTION_TYPE_REGULAR = 0
SUBSCRIPTION_TYPE_FREE = 1
SUBSCRIPTION_TYPE_NEW = 3
SUBSCRIPTION_TYPE_TEST_USER = 999


SUBSCRIPTION_TYPE = (
    (SUBSCRIPTION_TYPE_REGULAR, 'Regular'),
    (SUBSCRIPTION_TYPE_FREE, 'Free'),
    (SUBSCRIPTION_TYPE_NEW, 'New User'),
    (SUBSCRIPTION_TYPE_TEST_USER, 'Test User'),
)

SUBSCRIPTION_TYPE_DEFAULT = SUBSCRIPTION_TYPE_REGULAR

CC_TYPE_NONE = 0
CC_TYPE_VISA = 4
CC_TYPE_AMEX = 3
CC_TYPE_MC = 5
CC_TYPE_DISC = 6

# add our different credit card types...
CC_TYPES = (
    (CC_TYPE_NONE, 'None'),
    (CC_TYPE_AMEX, 'AMEX'),
    (CC_TYPE_VISA, 'Visa'),
    (CC_TYPE_MC, 'Mastercard'),
    (CC_TYPE_DISC, 'Discover'),
)

CC_DISPLAY = {
    CC_TYPE_NONE: 'None',
    CC_TYPE_AMEX: 'American Express',
    CC_TYPE_VISA: 'Visa',
    CC_TYPE_MC: 'Mastercard',
    CC_TYPE_DISC: 'Discover',
}

CC_DISPLAY_SHORT = {
    CC_TYPE_NONE: 'None',
    CC_TYPE_AMEX: 'AMEX',
    CC_TYPE_VISA: 'Visa',
    CC_TYPE_MC: 'MC',
    CC_TYPE_DISC: 'DISC',
}

USER_PLAN_CURRENT = 0
USER_PLAN_CANCELLING = 1
USER_PLAN_CANCELLED = 2

USER_PLAN_STATUS = (
    (USER_PLAN_CURRENT, 'Current'),
    (USER_PLAN_CANCELLING, 'Cancelling'),
    (USER_PLAN_CANCELLED, 'Cancelled'),
)

USER_PLAN_STATUS_DEFAULT = 0


# add our different credit card types...
BILLING_FREQUENCY_MONTHS = 0
BILLING_FREQUENCY_YEARS = 1
BILLING_FREQUENCY = (
    (BILLING_FREQUENCY_MONTHS, 'Monthly'),
    (BILLING_FREQUENCY_YEARS, 'Yearly'),
)


# content types
CONTENT_TYPES = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}

PROGRAM_IMAGE_FORMAT = {
    'size': (250, 250),
    'quality': 80,
    'format': 'png',
    'raw_path': 'programs/%s/raw',
    'path': 'programs/%s/'
}
