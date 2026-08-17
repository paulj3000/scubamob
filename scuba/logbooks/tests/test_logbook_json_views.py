import json

from django.test import TestCase

from scuba.accounts.models import User
from scuba.logbooks.models import LogbookFolder


class TestLogbookFoldersJson(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='folderowner@nowhere.com', username='folderowner', password='tester1234',
            first_name='Folder', last_name='Owner')
        self.other = User.objects.create_user(
            email='folderother@nowhere.com', username='folderother', password='tester1234',
            first_name='Folder', last_name='Other')

        self.owner_folder = LogbookFolder.objects.create(user=self.owner, name='Training')
        self.other_folder = LogbookFolder.objects.create(user=self.other, name='Wrecks')

    def test_requires_login(self):
        response = self.client.get('/logbooks/json/logbookfolders')

        self.assertEqual(response.status_code, 302)

    def test_get_lists_only_the_callers_own_folders(self):
        self.client.force_login(self.owner)

        response = self.client.get('/logbooks/json/logbookfolders')

        self.assertEqual(response.status_code, 200)
        names = [f['name'] for f in response.json()['folders']]
        self.assertIn('Training', names)
        self.assertNotIn('Wrecks', names)

    def test_post_creates_a_new_folder_for_the_caller(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            '/logbooks/json/logbookfolders',
            data=json.dumps({'foldername': 'Photography'}),
            content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            LogbookFolder.objects.filter(user=self.owner, name='Photography').exists())
        names = [f['name'] for f in response.json()['folders']]
        self.assertIn('Photography', names)


class TestLogbookFolderLogsJson(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='folderlogsowner@nowhere.com', username='folderlogsowner',
            password='tester1234', first_name='Folder', last_name='Owner')
        self.other = User.objects.create_user(
            email='folderlogsother@nowhere.com', username='folderlogsother',
            password='tester1234', first_name='Folder', last_name='Other')

        self.owner_folder = LogbookFolder.objects.create(user=self.owner, name='Training')

    def test_requires_login(self):
        response = self.client.get(
            '/logbooks/json/logbookfolderlogs', {'id': self.owner_folder.pk})

        self.assertEqual(response.status_code, 302)

    def test_returns_the_callers_own_folder(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            '/logbooks/json/logbookfolderlogs', {'id': self.owner_folder.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Training')

    def test_cannot_view_another_users_folder(self):
        self.client.force_login(self.other)

        response = self.client.get(
            '/logbooks/json/logbookfolderlogs', {'id': self.owner_folder.pk})

        self.assertEqual(response.status_code, 404)
