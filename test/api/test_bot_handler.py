import base64
import hashlib
import hmac
import json

import mock

from config import Config
from test.bot_test_base import BotTestBase
from test.test_base import TestBase


class BotHandlerTest(BotTestBase):
    @staticmethod
    def _generate_signature(api_key, body):
        return base64.b16encode(hmac.new(str(api_key), body, hashlib.sha1).digest())

    def test_no_signature(self):
        self.api_call('post', '/incoming', status=403)

    def test_invalid_signature(self):
        self.api_call('post', '/incoming', headers={'X-Kik-Signature': 'foobar'}, status=403)

    def test_data_not_json(self):
        body = 'yolo'
        self.api_call('post', '/incoming', headers={
            'X-Kik-Signature': self._generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=400)

    def test_no_messages(self):
        body = json.dumps({})
        self.api_call('post', '/incoming', headers={
            'X-Kik-Signature': self._generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=400)

    def test_messages_not_list(self):
        body = json.dumps({
            'messages': 'yolo'
        })
        self.api_call('post', '/incoming', headers={
            'X-Kik-Signature': self._generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=400)

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_zero_messages(self, queue):
        body = json.dumps({
            'messages': []
        })
        self.api_call('post', '/incoming', headers={
            'X-Kik-Signature': self._generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=200)

        self.assertEqual(queue.call_count, 0)

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_one_message(self, queue):
        message = {'type': 'text'}
        body = json.dumps({
            'messages': [message]
        })
        self.api_call('post', '/incoming', headers={
            'X-Kik-Signature': self._generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=200)

        self.assertEqual(queue.call_count, 1)
        self.assertEqual(queue.call_args[0][0], 'incoming')

        self.assertEqual(queue.return_value.add.call_count, 1)

        add = queue.return_value.add
        tasks = add.call_args[0][0]

        self.assertEqual(tasks[0].url, '/tasks/incoming')
        self.assertEqual(json.loads(tasks[0].payload), {'message': message})

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_batch_messages(self, queue):
        message0 = {'type': 'text'}
        message1 = {'type': 'text'}

        body = json.dumps({
            'messages': [message0] * Config.MAX_TASKQUEUE_BATCH_SIZE + [message1]
        })
        self.api_call('post', '/incoming', headers={
            'X-Kik-Signature': self._generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=200)

        self.assertEqual(queue.call_count, 2)
        self.assertEqual(queue.call_args_list[0][0][0], 'incoming')
        self.assertEqual(queue.call_args_list[1][0][0], 'incoming')

        self.assertEqual(queue.return_value.add.call_count, 2)

        add = queue.return_value.add
        tasks0 = add.call_args_list[0][0][0]
        tasks1 = add.call_args_list[1][0][0]

        self.assertEqual(len(tasks0), Config.MAX_TASKQUEUE_BATCH_SIZE)
        self.assertEqual(len(tasks1), 1)

        for task in tasks0:
            self.assertEqual(task.url, '/tasks/incoming')
            self.assertEqual(json.loads(task.payload), {'message': message0})

        for task in tasks1:
            self.assertEqual(task.url, '/tasks/incoming')
            self.assertEqual(json.loads(task.payload), {'message': message1})


class IncomingMessageTaskTest(TestBase):
    def setUp(self):
        super(IncomingMessageTaskTest, self).setUp()

        self.headers = {'X-AppEngine-TaskName': 'foo'}

    def test_no_message_param_loud_failure_if_not_task(self):
        self.api_call('post', '/tasks/incoming', status=400)

    def test_no_message_param_silent_failure_if_task(self):
        self.api_call('post', '/tasks/incoming', headers=self.headers, status=200)

    @mock.patch('kik.KikApi.send_messages')
    def test_not_allowed_type(self, send_messages):
        self.api_call('post', '/tasks/incoming', data={
            'message': {'type': 'unknown-type'}
        }, status=200)

        self.assertEqual(send_messages.call_count, 0)

    @mock.patch('kik.KikApi.send_messages')
    def test_mentioning_another_bot(self, send_messages):
        self.api_call('post', '/tasks/incoming', data={
            'message': {'type': 'text', 'from': 'foobar', 'mention': 'anotherbot'}
        }, status=200)

        self.assertEqual(send_messages.call_count, 0)
