"""
Tests for CODE_REVIEW.md §3 MEDIUM/LOW items fixed in this pass:
- item 18: duplicated, unwired ValidateUserId removed from apis/settings.py,
  the live iapis copy is unaffected.
- item 20: UserSettingSerializer.update() was copy-pasted from an unrelated
  serializer and called set_primary_email() instead of updating a setting.
- item 25: views/collections.py's IndexView.get_context_datas() (typo)
  is now get_context_data(), so Django actually calls it.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User, UserSetting


class TestValidateUserId(TestCase):
    """ item 18 -- only the live iapis copy remains """

    def setUp(self):
        self.user = User.objects.create_user(
            email='validate@nowhere.com', username='validateuser', password='tester1234',
            first_name='Validate', last_name='User')

    def test_valid_id_returns_true(self):
        client = APIClient()

        response = client.get(f'/iapi/settings/validate/{self.user.pk_as_str}')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['user']['is_valid'])

    def test_unknown_id_returns_false_with_400(self):
        client = APIClient()

        response = client.get('/iapi/settings/validate/00000000000000000000000000000000')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['user']['is_valid'])


class TestUserSettingSerializerUpdate(TestCase):
    """ item 20 -- update() now actually updates the setting's value
    instead of calling the unrelated set_primary_email(). """

    def test_update_persists_the_new_value(self):
        from scuba.accounts.serializers.settings import UserSettingSerializer

        user = User.objects.create_user(
            email='settingupdate@nowhere.com', username='settingupdateuser',
            password='tester1234', first_name='Setting', last_name='User')
        setting = UserSetting.objects.create(user=user, setting=0, value=1)

        serializer = UserSettingSerializer(setting, data={'value': 2}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        setting.refresh_from_db()
        self.assertEqual(setting.value, 2)


class TestCollectionsIndexView(TestCase):
    """ item 25 -- get_context_data (was get_context_datas, a typo Django
    silently never called) """

    def test_renders_for_a_logged_in_user(self):
        user = User.objects.create_user(
            email='collections@nowhere.com', username='collectionsuser',
            password='tester1234', first_name='Coll', last_name='User')
        client = APIClient()
        client.force_authenticate(user=user)
        client.force_login(user)

        response = client.get('/collections/')

        self.assertEqual(response.status_code, 200)
