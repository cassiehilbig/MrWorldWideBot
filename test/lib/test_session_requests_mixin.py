import json

from lib.session_requests_mixin import SessionRequestsMixin, InvalidTokenError, ExpiredSessionError, \
    InvalidChannelError, SessionError
from lib.utils import server_url
from test.test_base import TestBase


class SessionRequestsMixinTest(TestBase):
    def test_get_user_session_from_kik_code_data(self):
        self.route_urlfetch_response(
            'post', '{}/api/v1/botsworth/session'.format(server_url()), status=200, content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = SessionRequestsMixin()
        kik_code_data = {
            'session_id': 'abc'
        }
        response = mixin._get_user_session_from_kik_code_data(kik_code_data)

        self.assertEqual(response, {})

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(json.loads(self.request.payload()), {'session_id': 'abc'})

    def test_get_user_session_from_kik_code_data_with_username(self):
        self.route_urlfetch_response(
            'post', '{}/api/v1/botsworth/session'.format(server_url()), status=200, content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = SessionRequestsMixin()
        kik_code_data = {
            'session_id': 'abc'
        }
        response = mixin._get_user_session_from_kik_code_data(kik_code_data, 'eagerod')

        self.assertEqual(response, {})

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(json.loads(self.request.payload()), {'session_id': 'abc', 'username': 'eagerod'})

    def test_get_user_session_by_id(self):
        self.route_urlfetch_response(
            'post', '{}/api/v1/botsworth/session'.format(server_url()), status=200, content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = SessionRequestsMixin()
        response = mixin._get_user_session_by_id('abc')

        self.assertEqual(response, {})

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(json.loads(self.request.payload()), {'session_id': 'abc'})

    def test_get_user_session_from_by_id_with_username(self):
        self.route_urlfetch_response(
            'post', '{}/api/v1/botsworth/session'.format(server_url()), status=200, content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = SessionRequestsMixin()
        response = mixin._get_user_session_by_id('abc', 'eagerod')

        self.assertEqual(response, {})

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(json.loads(self.request.payload()), {'session_id': 'abc', 'username': 'eagerod'})

    def test_get_user_session_from_by_id_bad_response(self):
        self.route_urlfetch_response(
            'post', '{}/api/v1/botsworth/session'.format(server_url()), status=500, content='{}'
        )

        mixin = SessionRequestsMixin()
        self.assertRaises(InvalidTokenError, mixin._get_user_session_by_id, 'abc')

    def test_send_session_details(self):
        self.route_urlfetch_response(
            'put', '{}/api/v1/botsworth/session'.format(server_url()), status=200, content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = SessionRequestsMixin()
        mixin._send_session_details('abc', {'bot': 'somebotid'})

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(json.loads(self.request.payload()), {'session_id': 'abc', 'data': {'bot': 'somebotid'}})

    def test_send_session_details_expired_session(self):
        self.route_urlfetch_response(
            'put', '{}/api/v1/botsworth/session'.format(server_url()), status=400, content='{}'
        )

        mixin = SessionRequestsMixin()
        self.assertRaises(ExpiredSessionError, mixin._send_session_details, 'abc', {'bot': 'somebotid'})

    def test_send_session_details_invalid_token(self):
        self.route_urlfetch_response(
            'put', '{}/api/v1/botsworth/session'.format(server_url()), status=404, content='{}'
        )

        mixin = SessionRequestsMixin()
        self.assertRaises(InvalidTokenError, mixin._send_session_details, 'abc', {'bot': 'somebotid'})

    def test_send_channel_data(self):
        self.route_urlfetch_response(
            'post', '{}/api/v1/botsworth/channel'.format(server_url()), status=200, content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = SessionRequestsMixin()
        mixin._send_channel_data('abc', 'Success', 'eagerod')

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(json.loads(self.request.payload()), {
            'channel_id': 'abc', 'data': 'Success', 'username': 'eagerod'
        })

    def test_send_channel_data_invalid_channel(self):
        self.route_urlfetch_response(
            'post', '{}/api/v1/botsworth/channel'.format(server_url()), status=400, content='{}'
        )

        mixin = SessionRequestsMixin()
        self.assertRaises(InvalidChannelError, mixin._send_channel_data, 'abc', 'Success', 'eagerod')

    def test_send_link_action(self):
        self.route_urlfetch_response(
            'put', '{}/api/v1/botsworth/link_account'.format(server_url()), status=200, content='{}'
        )

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        mixin = SessionRequestsMixin()
        mixin._send_link_action('a@b.c', 'somebotid', 'eagerod')

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(json.loads(self.request.payload()), {
            'email': 'a@b.c', 'bot_id': 'somebotid', 'username': 'eagerod'
        })

    def test_send_link_action_bad_session(self):
        self.route_urlfetch_response(
            'put', '{}/api/v1/botsworth/link_account'.format(server_url()), status=400, content='{}'
        )

        mixin = SessionRequestsMixin()
        self.assertRaises(SessionError, mixin._send_link_action, 'a@b.c', 'somebotid', 'eagerod')
