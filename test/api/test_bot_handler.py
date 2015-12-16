import json
import mock

from test.test_base import TestBase
from lib.utils import generate_signature
from config import Config


class BotHandlerTest(TestBase):

    def test_no_signature(self):
        self.api_call('post', '/receive', status=403)

    def test_invalid_signature(self):
        self.api_call('post', '/receive', headers={'X-Kik-Signature': 'foobar'}, status=403)

    def test_data_not_json(self):
        body = 'yolo'
        self.api_call('post', '/receive', headers={
            'X-Kik-Signature': generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=400)

    def test_data_no_messages(self):
        body = json.dumps({})
        self.api_call('post', '/receive', headers={
            'X-Kik-Signature': generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=400)

    def test_data_messages_not_list(self):
        body = json.dumps({
            'messages': 'yolo'
        })
        self.api_call('post', '/receive', headers={
            'X-Kik-Signature': generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=400)

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_data_messages_empty(self, queue):
        body = json.dumps({
            'messages': []
        })
        self.api_call('post', '/receive', headers={
            'X-Kik-Signature': generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=200)

        self.assertEqual(queue.call_count, 0)

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_data_messages_one(self, queue):
        message = {'foo': 'bar'}
        body = json.dumps({
            'messages': [message]
        })
        self.api_call('post', '/receive', headers={
            'X-Kik-Signature': generate_signature(Config.BOT_API_KEY, body)
        }, data=body, status=200)

        self.assertEqual(queue.call_count, 1)
        self.assertEqual(queue.call_args[0][0], 'incoming')

        self.assertEqual(queue.return_value.add.call_count, 1)

        add = queue.return_value.add
        tasks = add.call_args[0][0]

        self.assertEqual(tasks[0].url, '/tasks/incoming')
        self.assertEqual(json.loads(tasks[0].payload), {'message': message})

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_data_messages_partition(self, queue):
        message0 = {'foo': 'bar'}
        message1 = {'baz': 'yolo'}

        body = json.dumps({
            'messages': [message0] * Config.MAX_TASKQUEUE_BATCH_SIZE + [message1]
        })
        self.api_call('post', '/receive', headers={
            'X-Kik-Signature': generate_signature(Config.BOT_API_KEY, body)
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

    @mock.patch('api.bot_handler.send_messages')
    @mock.patch('lib.bot_state_machine.state_machine.handle_message', return_value=['somemessage'])
    def test_success(self, handle_message, send_messages):
        message = {'from': 'someone'}
        self.api_call('post', '/tasks/incoming', data={
            'message': message
        })

        self.assertEqual(handle_message.call_count, 1)
        self.assertEqual(handle_message.call_args[0][0], 'someone')
        self.assertEqual(handle_message.call_args[0][1], message)

        self.assertEqual(send_messages.call_count, 1)
        self.assertEqual(send_messages.call_args[0][0], ['somemessage'])
        self.assertEqual(send_messages.call_args[1]['bot_name'], Config.BOT_USERNAME)
        self.assertEqual(send_messages.call_args[1]['bot_api_key'], Config.BOT_API_KEY)
