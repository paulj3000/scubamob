import random
import requests
from pprint import pprint

from django.core.management.base import BaseCommand

from scuba.accounts.models import User
from scuba.sitesettings.models import SystemApi

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u','--users', nargs='+', required=True)
        parser.add_argument('-c','--count', type=int, default=100)

    def handle(self, *args, **options):

        users = []
        chat_id = None
        count = options.get('count')

        for user in options.get('users'):
            try:
                pprint(User.objects.get(username=user).pk_as_str)
                users.append(User.objects.get(username=user).pk_as_str)
            except User.DoesNotExist:
                print(f"{user} is not a valid username")
                exit(1)

        # set the user count
        user_count = len(users)

        params = {
            'users': users,
            'userId': users[random.randint(0, user_count-1)]
        }

        try:
            chat = requests.get(f"{SystemApi.get_chat_server()}api/chats/lookup", params=params);
            retval = chat.json()

            if retval['chat']:
                chat_id = retval['chat']['id']
            else:
                try:
                    chat = requests.post(f"{SystemApi.get_chat_server()}api/chats/", json=params);
                    retval = chat.json()
                    chat_id = retval['chat']['id']
                except requests.exceptions.ConnectionError:
                    print("Chat server is not accessible")
                    exit(1)

        except requests.exceptions.ConnectionError:
            print("Chat server is not accessible")
            exit(1)

        for i in range(0, count):
            uid = random.randint(0, user_count-1)
            params = {
                'chatId': chat_id,
                'msg': {
                    'message': f"Message # {i}"
                },
                'userId': users[uid],
            }

            pprint(params)
            requests.post(f"{SystemApi.get_chat_server()}api/messages/add", json=params);

