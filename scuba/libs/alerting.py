import requests

from scuba.settings import ALERTING_SERVER


class Alerting:
    @staticmethod
    def send_buddy_request(userId, buddyUserId):
        url = f"{ALERTING_SERVER}/api/alerts/buddies/request"

        to_send = {
            'userId': userId,
            'buddyUserId': buddyUserId,
        }

        requests.post(url, json=to_send, timeout=5)
