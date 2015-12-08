import json

from google.appengine.api import urlfetch

from lib.utils import server_url


class BotDashboardRequestMixin(object):
    """
    State that has the framework to communicate with the `bot-dashboard` in order to manipulate users' session objects.
    This is a next-tier abstract class, since it still doesn't implement `type`
    """
    @staticmethod
    def _bot_dashboard_urlfetch(method, route, payload_json=None):
        """
        A wrapper around urlfetch that fills in a bunch of common values between all bot-dashboard requests.
        :param method:
        :param route:
        :param payload_json:
        :return:
        """
        return urlfetch.fetch(
            '{}/api/v1/botsworth{}'.format(server_url(), route),
            method=method,
            follow_redirects=False,
            payload=json.dumps(payload_json) if payload_json else None,
            headers={
                'Content-Type': 'application/json'
            }
        )
