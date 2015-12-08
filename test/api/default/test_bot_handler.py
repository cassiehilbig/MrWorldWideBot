import json

import mock

from test.botsworth_test_base import BotsworthTestBase
from const import MessageType
from config import Config
from api.default.bot_handler import IncomingMessageTask
from model.bot_user import BotUser


class BotHandlerTest(BotsworthTestBase):

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_success(self, queue):
        incoming_message = {'from': 'person', 'type': MessageType.TEXT, 'body': 'haaaaay'}

        # No message should be sent directly
        self.bot_call([incoming_message], [])

        self.assertEqual(queue.call_count, 1)
        self.assertEqual(queue.call_args[0][0], 'incoming')

        self.assertEqual(queue.return_value.add.call_count, 1)

        add = queue.return_value.add
        tasks = add.call_args[0][0]

        self.assertEqual(tasks[0].url, '/tasks/incoming')
        self.assertEqual(json.loads(tasks[0].payload), {'message': incoming_message})

    @mock.patch('google.appengine.api.taskqueue.Queue', return_value=mock.MagicMock())
    def test_success_batch(self, queue):
        incoming_message0 = {'from': 'person', 'type': MessageType.TEXT, 'body': 'haaaaay'}
        incoming_message1 = {'from': 'person', 'type': MessageType.TEXT, 'body': 'yolo'}

        # No message should be sent directly
        self.bot_call([incoming_message0] * Config.MAX_TASKQUEUE_BATCH_SIZE + [incoming_message1], [])

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
            self.assertEqual(json.loads(task.payload), {'message': incoming_message0})

        for task in tasks1:
            self.assertEqual(task.url, '/tasks/incoming')
            self.assertEqual(json.loads(task.payload), {'message': incoming_message1})

    def test_signature_failure(self):
        incoming_message = {'from': 'person', 'type': MessageType.TEXT, 'body': 'haaaaay'}
        self.bot_call([incoming_message], auto_generate_signature=False, status=403)


class IncomingMessageTaskTest(BotsworthTestBase):

    def test_missing_param(self):
        self.api_call('post', '/tasks/incoming', status=400)

    @mock.patch('api.default.bot_handler.send_messages')
    @mock.patch('lib.botsworth_state_machine.state_machine.handle_message', return_value=['somemessage'])
    def test_success(self, handle_message, send_messages):
        message = {
            'type': 'text',
            'from': 'someone',
            'body': 'yolo'
        }
        self.api_call('post', '/tasks/incoming', data={
            'message': message
        })

        self.assertEqual(handle_message.call_count, 1)
        self.assertEqual(handle_message.call_args[0][0], BotUser.get_by_id('someone'))
        self.assertEqual(handle_message.call_args[0][1], message)

        self.assertEqual(send_messages.call_count, 1)
        self.assertEqual(send_messages.call_args[0][0], ['somemessage'])

    @mock.patch('api.default.bot_handler.send_messages')
    def test_send_messages(self, send_messages):
        self.set_urlfetch_response(status=200, content='{}')
        messages = [{'from': 'person', 'type': MessageType.TEXT, 'body': 'haaaaay'}]
        IncomingMessageTask._send_messages(messages)

        self.assertEqual(send_messages.call_count, 1)
        self.assertEqual(send_messages.call_args[0][0], messages)
