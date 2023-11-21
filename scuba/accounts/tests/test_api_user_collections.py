"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import date
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.divesites.models import Divesite


class TestUserCollectionsAPI(TestCase):
    fixtures = ["test_users.json", "test_collections.json", "test_divesites.json"]

    def test_create_public_collection(self):
        """
        Test create public collection
        """
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'name': 'test collection',
            'is_public': True
        }

        url = f'/api/collections/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)

        collections = response.json()
        self.assertIsNotNone(collections)

        self.assertTrue(collections['is_public'])
        self.assertEqual(collections['name'], 'test collection')

    def test_create_private_collection(self):
        """
        Test create private collection
        """
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'name': 'test collection',
            'is_public': False
        }

        url = f'/api/collections/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)

        collections = response.json()
        self.assertIsNotNone(collections)

        self.assertFalse(collections['is_public'])
        self.assertEqual(collections['name'], 'test collection')

    def test_add_to_collection_1(self):
        """
        Test create private collection
        """
        # get the user and create a collection
        user = User.objects.get(email='foo@nowhere.com')
        collection = user.create_collection('test', True)

        # get the divesite
        divesite = Divesite.objects.all().first()

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'instance_id': divesite.id,
            'instance_type': 0,     # divesite
            'is_active': True,
        }

        url = f'/api/collections/{collection.pk_as_str}/add'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)

        item = response.json()
        self.assertIsNotNone(item['instance_id'])
        self.assertIsNotNone(item['instance_type'])
        self.assertTrue(item['is_active'])

    def test_add_to_collection_404(self):
        """
        Test create private collection
        """
        # get the user and create a collection
        user = User.objects.get(email='foo@nowhere.com')
        collection = user.create_collection('test', True)

        # get the divesite
        divesite = Divesite.objects.all().first()

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'instance_id': divesite.id,
            'instance_type': 0,     # divesite
        }

        # sending in divesite.pk_as_str on purpose. No collection
        # will exists so this should throw a 404
        url = f'/api/collections/{divesite.pk_as_str}/add'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 404)

    def test_get_collection(self):
        """
        Test create private collection
        """
        # get the user and create a collection
        user = User.objects.get(email='foo@nowhere.com')
        collection = user.create_collection('test', True)

        client = APIClient()
        client.force_authenticate(user=user)

        # sending in divesite.pk_as_str on purpose. No collection
        # will exists so this should throw a 404
        url = f'/api/collections/'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        collections = response.json()
        self.assertIsNotNone(collections.get('collections'))
        self.assertEqual(len(collections.get('collections')), 1)

    def test_get_collection_with_divesite(self):
        """
        Test get a collection with a divesite
        """
        # get the user and create a collection
        user = User.objects.get(email='foo@nowhere.com')
        collection = user.create_collection('test', True)

        # get the divesite
        divesite = Divesite.objects.all().first()
        collection.items.create(instance_id=divesite.id, instance_type=0)

        client = APIClient()
        client.force_authenticate(user=user)

        # sending in divesite.pk_as_str on purpose. No collection
        # will exists so this should throw a 404
        url = f'/api/collections/?instance={divesite.pk_as_str}'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        collections = response.json()
        self.assertIsNotNone(collections.get('collections'))
        self.assertEqual(len(collections.get('collections')), 1)
        self.assertIsNotNone(collections['collections'][0].get('is_active'))
        self.assertTrue(collections['collections'][0]['is_active'])
