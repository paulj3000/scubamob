"""
Tests for scuba.accounts.forms.SettingsForm/PasswordForm, and their live
wiring at /settings/account and /settings/password/.

These forms used to declare Meta.model = django.contrib.auth.models.User
(Django's default user model) instead of this project's swapped
AUTH_USER_MODEL, scuba.accounts.models.User -- CODE_REVIEW.md §3.1.
"""
from django.test import TestCase

from scuba.accounts.forms import PasswordForm, SettingsForm
from scuba.accounts.models import User


class TestSettingsForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='settingsform@nowhere.com', username='settingsformuser',
            password='tester1234', first_name='Old', last_name='Name')

    def test_uses_the_projects_real_user_model(self):
        self.assertIs(SettingsForm.Meta.model, User)

    def test_updates_the_real_user_instance(self):
        form = SettingsForm(
            {'first_name': 'New', 'last_name': 'Name', 'email': 'updated@nowhere.com'},
            instance=self.user)

        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()

        self.assertEqual(saved.pk, self.user.pk)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.email, 'updated@nowhere.com')

    def test_first_name_over_the_models_max_length_is_rejected(self):
        form = SettingsForm(
            {'first_name': 'x' * 41, 'last_name': 'Name', 'email': self.user.email},
            instance=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_duplicate_email_is_rejected_by_the_real_models_unique_constraint(self):
        User.objects.create_user(
            email='taken@nowhere.com', username='otherformuser', password='tester1234',
            first_name='Other', last_name='User')

        form = SettingsForm(
            {'first_name': 'New', 'last_name': 'Name', 'email': 'taken@nowhere.com'},
            instance=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class TestPasswordForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='passwordform@nowhere.com', username='passwordformuser',
            password='tester1234', first_name='Test', last_name='User')

    def test_uses_the_projects_real_user_model(self):
        self.assertIs(PasswordForm.Meta.model, User)

    def test_updates_the_real_users_password(self):
        form = PasswordForm(
            {'password': 'newpassword123', 'password2': 'newpassword123'},
            instance=self.user)

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_mismatched_confirmation_is_rejected(self):
        form = PasswordForm(
            {'password': 'newpassword123', 'password2': 'somethingelse'},
            instance=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class TestSettingsViewsLive(TestCase):
    """ End-to-end coverage of the actual /settings/account and
    /settings/password/ routes these forms are wired into. """

    def setUp(self):
        self.user = User.objects.create_user(
            email='liveuser@nowhere.com', username='liveuser',
            password='tester1234', first_name='Live', last_name='User')
        self.client.force_login(self.user)

    def test_account_settings_get_renders(self):
        response = self.client.get('/settings/account')

        self.assertEqual(response.status_code, 200)

    def test_account_settings_post_updates_and_redirects(self):
        response = self.client.post('/settings/account', {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'liveuser@nowhere.com',
        })

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_password_settings_post_updates_and_redirects(self):
        response = self.client.post('/settings/password/', {
            'password': 'brandnewpassword1',
            'password2': 'brandnewpassword1',
        })

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('brandnewpassword1'))
