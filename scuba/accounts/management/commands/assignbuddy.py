from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from scuba.accounts.models import User

from scuba.accounts.models import UserBuddyRequest, UserBuddy


class Command(BaseCommand):
    def handle(self, *args, **options):
        ''' update all account guids '''

        me_user = User.objects.filter(email='first@user.com').first()

        for i in range(0, 100):

            email = f'xuser{i}@em{i}.com'
            buddy_user = User.objects.get(email=email)
            me_user.add_buddy(buddy_user)
