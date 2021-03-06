from __future__ import absolute_import

import json

import mock

from app import kik
from config import Config
from lib.utils import generate_signature
from test.test_base import TestBase


class BotTestBase(TestBase):
    @classmethod
    def setUpClass(cls):
        super(BotTestBase, cls).setUpClass()
        cls.send_messages_location = 'kik.KikApi.send_messages'
        cls.api_route = '/incoming'

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
                if kik.api_key is None:
                    raise AssertionError('Can\'t generate signature without bot api key.')
                headers['X-Kik-Signature'] = generate_signature(Config.BOT_API_KEY, post_data)

            self.api_call('POST', self.api_route, data=post_data, headers=headers, status=status)

            self.execute_tasks(queue='incoming')

            if expected_outgoing_messages:
                self.assertEqual(send_messages.call_count, 1)
                self.assertEqual(send_messages.call_args[0][0], expected_outgoing_messages)
            elif expected_outgoing_messages is not None:
                self.assertEqual(send_messages.call_count, 0)
