from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from scuba.accounts.models import User

from scuba.accounts.models import UserBuddyRequest, UserBuddy

class Command(BaseCommand):
    def handle(self, *args, **options):
        ''' update all account guids '''

        me_user = User.objects.all().first()

        for i in range(0, 100):

            username = f'xuser_{i}'
            email = f'xuser{i}@em{i}.com'
            try:
                new_user = User();
                new_user.first_name = f'test {i}'
                new_user.last_name = f'user {i}'
                new_user.date_of_birth = '1970-04-01'

                new_user.email = email
                new_user.set_password(f'tester{i}')
                new_user.save()

                # create the new account
                if me_user:
                    if not i % 10:
                        UserBuddyRequest.objects.create(user=new_user, buddy=me_user)
                    else:
                        UserBuddy.objects.create(buddy=new_user, user=me_user)
                        UserBuddy.objects.create(buddy=me_user, user=new_user)
            except IntegrityError:
                print(f"User {username} with email {email} already exists")
