from __future__ import absolute_import
import json
import mock

from test.test_base import TestBase
from lib.utils import generate_signature


class BotTestBase(TestBase):
    @classmethod
    def setUpClass(cls):
        super(BotTestBase, cls).setUpClass()
        cls.send_messages_location = None
        cls.api_route = None
        cls.bot_api_key = None

    def setUp(self):
        super(BotTestBase, self).setUp()
        if self.api_route is None or self.send_messages_location is None:
            raise AssertionError('Bot tests must set up api_route, and send_messages_location in setUpClass')

    def bot_call(self, incoming_messages, expected_outgoing_messages=None, auto_generate_signature=True, status=200):
        with mock.patch(self.send_messages_location) as send_messages:
            post_data = json.dumps({'messages': incoming_messages})

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
                self.assertEqual(send_messages.call_args[0][0], expected_outgoing_messages)
