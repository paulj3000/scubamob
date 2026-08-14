from django.test import TestCase

from scuba.accounts.models import User


class TestLogbookIndexView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='logbookviewer@nowhere.com', username='logbookviewer', password='tester1234',
            first_name='Log', last_name='Viewer')

    def test_index_requires_login(self):
        response = self.client.get('/logbooks/')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login'))

    def test_index_renders_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get('/logbooks/')

        self.assertEqual(response.status_code, 200)

    def test_dive_add_route_no_longer_exists(self):
        self.client.force_login(self.user)

        response = self.client.get('/logbooks/dives/edit/')

        self.assertEqual(response.status_code, 404)
