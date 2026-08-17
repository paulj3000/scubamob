from django.test import TestCase

from scuba.accounts.models import User
from scuba.equipment.forms import EquipmentForm


class TestEquipmentForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='formuser@nowhere.com', username='equipmentformuser', password='tester1234',
            first_name='Form', last_name='User')

    def test_save_returns_the_saved_instance(self):
        form = EquipmentForm(data={
            'addone': 'reg', 'addtwo': 'bcd', 'addthree': 'fins', 'addfour': 'mask',
        })
        form.user = self.user

        self.assertTrue(form.is_valid())
        obj = form.save()

        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.user, self.user)
