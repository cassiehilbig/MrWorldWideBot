import json

from google.appengine.api import urlfetch

from lib.bot_dashboard_request_mixin import BotDashboardRequestMixin
from lib.utils import server_url
from test.test_base import TestBase


class BotDashboardRequestMixinTest(TestBase):
    def test_bot_dashboard_url_fetch(self):
        self.route_urlfetch_response('post', '{}/api/v1/botsworth/fake_route'.format(server_url()), status=200)

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = BotDashboardRequestMixin()
        response = mixin._bot_dashboard_urlfetch(urlfetch.POST, '/fake_route')

        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')

    def test_bot_dashboard_url_fetch_payload(self):
        self.route_urlfetch_response('post', '{}/api/v1/botsworth/fake_route'.format(server_url()), status=200)

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = BotDashboardRequestMixin()
        response = mixin._bot_dashboard_urlfetch(urlfetch.POST, '/fake_route', {
            'a_key': 'a_value'
        })

        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(self.request)
        self.assertEqual(json.loads(self.request.payload()), {'a_key': 'a_value'})
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
