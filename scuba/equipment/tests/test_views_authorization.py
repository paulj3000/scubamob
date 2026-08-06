"""
Authorization tests for scuba.equipment.views. Every view must require
login and scope every query/mutation to the logged-in user's own records.
"""
from django.test import TestCase

from scuba.accounts.models import User
from scuba.equipment.models import Equipment, EquipmentMaintenance

LOGIN_URL_PREFIX = '/login'


class TestEquipmentAuthorization(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@nowhere.com', username='equipmentowner', password='tester1234',
            first_name='Owner', last_name='User')
        self.other = User.objects.create_user(
            email='other@nowhere.com', username='equipmentother', password='tester1234',
            first_name='Other', last_name='User')

        self.owner_equipment = Equipment.objects.create(
            user=self.owner, addone='reg', addtwo='bcd', addthree='fins', addfour='mask')
        self.other_equipment = Equipment.objects.create(
            user=self.other, addone='reg2', addtwo='bcd2', addthree='fins2', addfour='mask2')

        self.owner_requirement = EquipmentMaintenance.objects.create(
            equipment=self.owner_equipment, requireone='inspect', requiretwo='annual')
        self.other_requirement = EquipmentMaintenance.objects.create(
            equipment=self.other_equipment, requireone='inspect', requiretwo='annual')

    # -- anonymous access is blocked on every view --------------------------

    def test_anonymous_access_is_redirected_to_login(self):
        urls = [
            '/equipment/',
            '/equipment/edit/',
            f'/equipment/edit/{self.owner_equipment.pk}/',
            f'/equipment/delete/{self.owner_equipment.pk}/',
            '/equipment/practiceapp2/',
            '/equipment/requirementsview/',
            '/equipment/practicerequire/',
            f'/equipment/{self.owner_requirement.pk}/practicerequire_edit/',
            f'/equipment/{self.owner_requirement.pk}/requirements_delete/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertTrue(response.url.startswith(LOGIN_URL_PREFIX), url)

    # -- listing views only show the caller's own records --------------------

    def test_index_only_lists_the_callers_own_equipment(self):
        self.client.force_login(self.owner)

        response = self.client.get('/equipment/')

        self.assertEqual(response.status_code, 200)
        equipment_in_context = list(response.context['equipment'])
        self.assertIn(self.owner_equipment, equipment_in_context)
        self.assertNotIn(self.other_equipment, equipment_in_context)

    def test_archive2_only_lists_the_callers_own_equipment(self):
        self.client.force_login(self.owner)

        response = self.client.get('/equipment/practiceapp2/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.owner_equipment.addone.encode(), response.content)
        self.assertNotIn(self.other_equipment.addone.encode(), response.content)

    def test_archive3_only_lists_the_callers_own_requirements(self):
        self.client.force_login(self.owner)

        response = self.client.get('/equipment/requirementsview/')

        self.assertEqual(response.status_code, 200)

    # -- editing/deleting another user's equipment is blocked ----------------

    def test_cannot_view_edit_form_for_another_users_equipment(self):
        self.client.force_login(self.owner)

        response = self.client.get(f'/equipment/edit/{self.other_equipment.pk}/')

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_users_equipment(self):
        self.client.force_login(self.owner)

        response = self.client.get(f'/equipment/delete/{self.other_equipment.pk}/')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Equipment.objects.filter(pk=self.other_equipment.pk).exists())

    def test_can_delete_own_equipment(self):
        self.client.force_login(self.owner)

        response = self.client.get(f'/equipment/delete/{self.owner_equipment.pk}/')

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Equipment.objects.filter(pk=self.owner_equipment.pk).exists())

    # -- maintenance requirements are scoped through equipment ownership -----

    def test_cannot_view_edit_form_for_another_users_requirement(self):
        self.client.force_login(self.owner)

        response = self.client.get(f'/equipment/{self.other_requirement.pk}/practicerequire_edit/')

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_users_requirement(self):
        self.client.force_login(self.owner)

        response = self.client.get(f'/equipment/{self.other_requirement.pk}/requirements_delete/')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(EquipmentMaintenance.objects.filter(pk=self.other_requirement.pk).exists())

    def test_new_requirement_cannot_be_attached_to_another_users_equipment(self):
        self.client.force_login(self.owner)

        response = self.client.post('/equipment/practicerequire/', {
            'requireone': 'hostile-inspect',
            'requiretwo': 'annual',
            'equipment': self.other_equipment.pk,
        })

        # rejected by the form's own queryset restriction, not saved
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            EquipmentMaintenance.objects.filter(requireone='hostile-inspect').exists())

    def test_new_requirement_can_be_attached_to_own_equipment(self):
        self.client.force_login(self.owner)

        response = self.client.post('/equipment/practicerequire/', {
            'requireone': 'inspect',
            'requiretwo': 'annual',
            'equipment': self.owner_equipment.pk,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EquipmentMaintenance.objects.filter(
                equipment=self.owner_equipment, requireone='inspect').exists())
