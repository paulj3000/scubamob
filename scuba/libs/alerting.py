import requests

from scuba.sitesettings.models import SystemApi


class Alerting:
    @staticmethod
    def send_buddy_request(userId, buddyUserId):
        url = SystemApi.get_alerting_buddy_request()

        to_send = {
            'userId': userId,
            'buddyUserId': buddyUserId,
        }

        requests.post(url, json=to_send)
