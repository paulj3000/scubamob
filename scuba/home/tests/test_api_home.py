"""
Tests for scuba.home.apis.GetHomescreenApi. Weather calls are mocked -- no
live WeatherAPI access.
"""
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User, UserFeed
from scuba.content.models import NewsArticle
from scuba.divesites.models import Divesite, DivesiteCheckin, DivesiteFavorite

WEATHER_PAYLOAD = {
    'location': {'name': 'Ocean Beach', 'region': 'California', 'country': 'USA'},
    'current': {'temp_f': 68},
}


class TestHomeAPI(TestCase):
    fixtures = ["test_divesites.json", "test_users.json"]

    def setUp(self):
        cache.clear()

    @patch('scuba.home.apis.Weather.get_current_by_q_param')
    def test_homescreen_calls_weather_api_once_then_uses_cache(self, mock_weather):
        mock_weather.return_value = dict(WEATHER_PAYLOAD)

        user = User.objects.get(email='foo@nowhere.com')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/home/?q=92107', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_weather.call_count, 1)

        # a second request for the same q_param must be served from the
        # cache -- the external Weather API must not be called again.
        mock_weather.return_value = dict(WEATHER_PAYLOAD)
        response = client.get('/api/home/?q=92107', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_weather.call_count, 1)

    @patch('scuba.home.apis.Weather.get_current_by_q_param')
    def test_homescreen_dashboard_widgets(self, mock_weather):
        mock_weather.return_value = dict(WEATHER_PAYLOAD)

        user = User.objects.get(email='foo@nowhere.com')
        buddy = User.objects.get(email='addbuddy@tester.com')
        user.add_buddy(buddy)

        site = Divesite.objects.get(url='white-point')
        DivesiteFavorite.objects.create(user=user, divesite=site)

        checkin = DivesiteCheckin.objects.create(user=buddy, divesite=site, rating=4)
        buddy.add_checkin_to_feed(checkin.id)

        NewsArticle.objects.create(
            title='Test News Article', user=user, content='<p>hello</p>',
            is_published=True)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/home/?q=92107', format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # favorites must be real, serialized divesite objects -- not the
        # bare id strings get_divesite_favorites() itself returns.
        favorites = data['divesites']['favorites']
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0]['id'], site.pk_as_str)
        self.assertIn('name', favorites[0])
        self.assertNotIn('stats', favorites[0])

        self.assertLessEqual(len(data['divesites']['list']), 6)

        activity = data['friends_activity']
        self.assertEqual(len(activity), 1)
        self.assertEqual(activity[0]['type'], 'CHECKIN')
        self.assertEqual(activity[0]['user']['username'], buddy.username)

        news = data['news']
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['title'], 'Test News Article')

    @patch('scuba.home.apis.Weather.get_current_by_q_param')
    def test_homescreen_friends_activity_excludes_non_buddies_and_private(self, mock_weather):
        mock_weather.return_value = dict(WEATHER_PAYLOAD)

        user = User.objects.get(email='foo@nowhere.com')
        stranger = User.objects.get(email='test3@tester.com')
        site = Divesite.objects.get(url='white-point')

        checkin = DivesiteCheckin.objects.create(user=stranger, divesite=site, rating=4)
        UserFeed.objects.create(user=stranger, instance_type=1, instance_id=checkin.id)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/home/?q=92107', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['friends_activity'], [])
