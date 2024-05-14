import random
import requests

from django.core.management.base import BaseCommand

from scuba.accounts.models import User
from scuba.sitesettings.models import SystemApi, ChatApi


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', nargs='+', required=True)
        parser.add_argument('-m', '--messages', type=int, default=100)
        parser.add_argument('-c', '--count', type=int, default=1)

    def handle(self, *args, **options):

        chat_count = options.get('count')
        messages = options.get('messages')
        print(f"Chat count: {chat_count}")

        user_list = []
        chat_id = None

        for user in options.get('users'):
            try:
                user_list.append(User.objects.get(email=user).pk_as_str)
            except User.DoesNotExist:
                print(f"{user} is not a valid username")
                exit(1)

        # get the user count
        user_count = len(user_list)

        for j in range(0, chat_count):
            print(f"Chat: {j}")
            # set the user count
            users = []
            if user_count >= 3:
                rnd = random.randint(3, user_count - 1)
                while len(users) < rnd:
                    rnd2 = random.randint(0, user_count - 1)
                    if user_list[rnd2] not in users:
                        users.append(user_list[rnd2])
            else:
                users = user_list

            params = {
                'users': users,
                'userId': users[random.randint(0, len(users) - 1)]
            }

            try:
                chat = ChatApi.chat_lookup(params)
                retval = chat.json()

                if retval['chat']:
                    chat_id = retval['chat']['id']
                else:
                    try:
                        retval = ChatApi.create_chat(params)
                        chat_id = retval['chat']['id']
                    except requests.exceptions.ConnectionError:
                        print("Chat server is not accessible")
                        exit(1)

            except requests.exceptions.ConnectionError:
                print("Chat server is not accessible")
                exit(1)

            chat_user_count = len(users)
            for i in range(0, messages):

                print(f"Chat: {j}: Message {i}")
                uid = random.randint(0, chat_user_count - 1)
                params = {
                    'chatId': chat_id,
                    'msg': {
                        'message': f"Message # {i}"
                    },
                    'userId': users[uid],
                }

                requests.post(f"{SystemApi.get_chat_server()}/api/messages/add", json=params)
