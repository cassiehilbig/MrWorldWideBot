from __future__ import absolute_import
import json
import mock

from kik.resource import Resource
from test.test_base import TestBase
from lib.utils import generate_signature
from config import Config


class BotTestBase(TestBase):
    @classmethod
    def setUpClass(cls):
        super(BotTestBase, cls).setUpClass()
        cls.send_messages_location = 'kik.api.MessageApi.send'
        cls.api_route = '/incoming'
        Config.BOT_API_KEY = 'test'
        cls.bot_api_key = 'test'

    def setUp(self):
        super(BotTestBase, self).setUp()
        if self.api_route is None or self.send_messages_location is None:
            raise AssertionError('Bot tests must set up api_route, and send_messages_location in setUpClass')

    def bot_call(self, incoming_messages, expected_outgoing_messages=None, auto_generate_signature=True, status=200):
        with mock.patch(self.send_messages_location) as send_messages:
            messages = [m.to_json() for m in incoming_messages]
            post_data = json.dumps({'messages': messages})

            headers = {
                'Content-Type': 'application/json'
            }

            if auto_generate_signature:
                if self.bot_api_key is None:
                    raise AssertionError('Can\'t generate signature without bot api key.')
                headers['X-Kik-Signature'] = generate_signature(self.bot_api_key, post_data)

            self.api_call('POST', self.api_route, data=post_data, headers=headers, status=status)

            self.execute_tasks(queue='incoming')

            if expected_outgoing_messages:
                self.assertEqual(send_messages.call_count, 1)
                # print expected_outgoing_messages[0].__dict__
                # print send_messages.call_args[0][0][0].__dict__
                # self.assertItemsEqual(send_messages.call_args[0][0], expected_outgoing_messages)
            elif expected_outgoing_messages is not None:
                self.assertEqual(send_messages.call_count, 0)
