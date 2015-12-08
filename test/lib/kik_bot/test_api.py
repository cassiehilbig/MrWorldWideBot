import json
from base64 import b64decode

from test.test_base import TestBase
from const import MessageType
from lib.kik_bot import send_messages, get_user_info, SendMessagesError, UserInfoError
from lib.utils import server_url, messaging_url


class KikBotApiTest(TestBase):
    def test_send_messages(self):
        self.route_urlfetch_response('post', messaging_url(), status=200, content='{}')

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        msgs = [{
            'type': MessageType.TEXT,
            'to': 'eagerod',
            'body': 'Sometext',
            'suggestedResponses': ['A', 'B', 'C']
        }]

        response = send_messages(msgs, 'mybotusername', 'mybotapikey')

        self.assertEqual(response, {})

        self.assertIsNotNone(self.request)
        self.assertEqual(json.loads(self.request.payload()), {'messages': msgs})
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(self.request.header(1).key(), 'Authorization')
        auth_header = self.request.header(1).value()
        self.assertEqual(auth_header.split()[0], 'Basic')
        self.assertEqual(b64decode(auth_header.split()[1]), 'mybotusername:mybotapikey')

    def test_send_messages_failure(self):
        self.route_urlfetch_response('post', messaging_url(), status=400, content=json.dumps({'error': 'BadRequest'}))

        msgs = [{
            'type': MessageType.TEXT,
            'to': 'eagerod',
            'body': 'Sometext'
        }]

        self.assertRaises(SendMessagesError, send_messages, msgs, 'mybotusername', 'mybotapikey')

    def test_get_user_info(self):
        self.route_urlfetch_response('get', '{}/api/v1/user/eagerod'.format(server_url()), status=200, content='{}')

        self.request = None

        def callback(request):
            self.request = request

        self.set_urlfetch_request_callback(callback)

        response = get_user_info('eagerod', 'mybotusername', 'mybotapikey')

        self.assertEqual(response, {})

        self.assertIsNotNone(self.request)
        self.assertEqual(self.request.header(0).key(), 'Content-Type')
        self.assertEqual(self.request.header(0).value(), 'application/json')
        self.assertEqual(self.request.header(1).key(), 'Authorization')
        auth_header = self.request.header(1).value()
        self.assertEqual(auth_header.split()[0], 'Basic')
        self.assertEqual(b64decode(auth_header.split()[1]), 'mybotusername:mybotapikey')

    def test_get_user_info_failure(self):
        self.route_urlfetch_response(
            'get',
            '{}/api/v1/user/eagerod'.format(server_url()),
            status=400,
            content=json.dumps({'error': 'BadRequest'})
        )

        self.assertRaises(UserInfoError, get_user_info, 'eagerod', 'mybotusername', 'mybotapikey')
