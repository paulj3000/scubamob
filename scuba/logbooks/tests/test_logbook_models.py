from django.test import TestCase

from scuba.accounts.models import User
from scuba.logbooks.models import Logbook


class TestLogbookGetLogs(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='logbookowner@nowhere.com', username='logbookowner', password='tester1234',
            first_name='Log', last_name='Owner')
        self.other = User.objects.create_user(
            email='logbookother@nowhere.com', username='logbookother', password='tester1234',
            first_name='Log', last_name='Other')

        self.owner_log = Logbook.objects.create(
            user=self.owner, name='My Logbook', description='desc')
        self.other_log = Logbook.objects.create(
            user=self.other, name='Other Logbook', description='desc')

    def test_get_logs_returns_only_the_users_own_logbooks(self):
        result = Logbook.get_logs(self.owner)

        self.assertIn(self.owner_log, result)
        self.assertNotIn(self.other_log, result)
