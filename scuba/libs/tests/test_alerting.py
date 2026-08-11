"""
Tests for scuba.libs.alerting.Alerting.send_buddy_request. requests.post is
mocked -- no live alerting service access.

Previously this called sitesettings.SystemApi.get_alerting_buddy_request(),
which looked up a SystemApi key ('ALERTING_BUDDY_REQUEST') that never
existed anywhere -- always raising InvalidConfigurationException. The real,
fixture-configured endpoint path lived under the sibling AlertingApi model
instead (key 'BUDDY_REQUEST' = '/api/alerts/buddies/request'), just never
wired up correctly (see MODERNIZATION_ROADMAP.md item 9).
"""
from unittest.mock import patch

from django.test import SimpleTestCase

from scuba.libs.alerting import Alerting
from scuba.settings import ALERTING_SERVER


class TestAlerting(SimpleTestCase):
    @patch('scuba.libs.alerting.requests.post')
    def test_send_buddy_request_posts_to_the_settings_based_url(self, mock_post):
        Alerting.send_buddy_request('user-1', 'user-2')

        mock_post.assert_called_once_with(
            f"{ALERTING_SERVER}/api/alerts/buddies/request",
            json={'userId': 'user-1', 'buddyUserId': 'user-2'},
            timeout=5)
