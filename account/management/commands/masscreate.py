#===============================================================================
# updateaccountguid.py
#
# Update Account Guid
#
# Authors: Pauljames "The Juggernaut" Dimitriu
#===============================================================================
import time
import pprint
import random
from optparse import make_option

from django.utils import simplejson
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings

from account.models import Account, UserFriendRequest, UserFriend

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

        for i in range(0, 100):
       
            new_user    = User();
            new_user.first_name     = 'test'
            new_user.last_name     = 'user'

            new_user.username    = "xuser%i" % i
            new_user.email    = "xuser%i@em%i.com" % (i, i)
            new_user.save()

            new_user.set_unusable_password()

            ## create the new account
            Account.objects.create(user=new_user)
            

            if not i % 10:
                UserFriendRequest.objects.create(user=new_user, friend_id=1, email='paulj1999@yahoo.com')
            else:
                UserFriend.objects.create(friend=new_user, user_id=1)

