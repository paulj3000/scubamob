import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        ''' update all account guids '''
        print("Is this building .... ", os.environ.get('IS_BUILDING', -999))
