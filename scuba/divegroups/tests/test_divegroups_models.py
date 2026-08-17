from django.db import IntegrityError, transaction
from django.test import TestCase

from scuba.accounts.models import User
from scuba.divegroups.models import Group, GroupUser


class TestGroupIsUserAdmin(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='groupowner@nowhere.com', username='groupowner', password='tester1234',
            first_name='Group', last_name='Owner')
        self.admin_member = User.objects.create_user(
            email='groupadmin@nowhere.com', username='groupadmin', password='tester1234',
            first_name='Group', last_name='Admin')
        self.regular_member = User.objects.create_user(
            email='groupmember@nowhere.com', username='groupmember', password='tester1234',
            first_name='Group', last_name='Member')

        self.group = Group.objects.create(user=self.owner, title='Wreck Divers')
        GroupUser.objects.create(group=self.group, user=self.admin_member, isadmin=True)
        GroupUser.objects.create(group=self.group, user=self.regular_member, isadmin=False)

    def test_admin_member_is_admin(self):
        self.assertTrue(self.group.is_user_admin(self.admin_member))

    def test_regular_member_is_not_admin(self):
        self.assertFalse(self.group.is_user_admin(self.regular_member))

    def test_non_member_is_not_admin(self):
        outsider = User.objects.create_user(
            email='outsider@nowhere.com', username='outsider', password='tester1234',
            first_name='Out', last_name='Sider')
        self.assertFalse(self.group.is_user_admin(outsider))


class TestGroupUserDefaults(TestCase):
    def test_isadmin_defaults_to_false(self):
        owner = User.objects.create_user(
            email='defaultowner@nowhere.com', username='defaultowner', password='tester1234',
            first_name='Default', last_name='Owner')
        member = User.objects.create_user(
            email='defaultmember@nowhere.com', username='defaultmember', password='tester1234',
            first_name='Default', last_name='Member')
        group = Group.objects.create(user=owner, title='Reef Explorers')

        group_user = GroupUser.objects.create(group=group, user=member)

        self.assertFalse(group_user.isadmin)


class TestGroupTitleUniqueness(TestCase):
    def setUp(self):
        self.first_owner = User.objects.create_user(
            email='firstowner@nowhere.com', username='firstowner', password='tester1234',
            first_name='First', last_name='Owner')
        self.second_owner = User.objects.create_user(
            email='secondowner@nowhere.com', username='secondowner', password='tester1234',
            first_name='Second', last_name='Owner')

    def test_different_users_can_share_a_group_title(self):
        Group.objects.create(user=self.first_owner, title='Night Divers')
        Group.objects.create(user=self.second_owner, title='Night Divers')

        self.assertEqual(Group.objects.filter(title='Night Divers').count(), 2)

    def test_same_user_cannot_reuse_a_group_title(self):
        Group.objects.create(user=self.first_owner, title='Night Divers')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Group.objects.create(user=self.first_owner, title='Night Divers')
