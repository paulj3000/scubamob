#===============================================================================
# updateaccountguid.py
#
# Update Account Guid
#
# Authors: Pauljames "The Juggernaut" Dimitriu
#===============================================================================
import time
import pprint
from optparse import make_option

from django.utils import simplejson
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings

from account.models import Account

class Command(BaseCommand):

    '''
    option_list = BaseCommand.option_list + (
        make_option("--rule", dest="rule"),
        make_option("--username", dest="username"),
        make_option("--newusername", dest="newusername"),
        make_option("--serviceid", dest="serviceid"),
        make_option("--run", dest="run", action="store_true")
    )
    '''

    def handle(self, *args, **options):
        ''' update all account guids '''
        accounts    = Account.objects.filter(guid=None)

        for a in accounts:
            ### save the account id
            a.guid=a.init_guid()
            a.created='2013-09-15 02:04:03'
            a.modified='2013-09-15 02:04:03'
            a.save()

        ## let's check for straggler users
        for user in User.objects.all():
            time.sleep(1)
            try:
                Account.objects.get(user=user)
            except:
                Account.objects.create(user=user)
