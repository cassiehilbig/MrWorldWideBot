from datetime import datetime
import json
import mock
import pickle

from test.botsworth_test_base import BotsworthTestBase
from lib.botsworth_state_machine import state_machine
from const import MessageType
from lib.datetime_utils import datetime_to_utc_timestamp_millis
from lib.states.default import DefaultStateStrings, DefaultState
from lib.session_requests_mixin import InvalidTokenError, InvalidChannelError
from lib.states.login_with_kik.login_with_kik_flow import LoginWithKikStrings, LoginWithKikChannelMessages
from lib.state_machine import State, PopTransition
from lib.states.state_types import StateTypes
from model import BotUser, UserSessionMap


class AlwaysPoppingTestState(State):
    @staticmethod
    def type():
        return 'pop-state'

    def on_message(self, message):
        return PopTransition([])


class TestLoginFlow(BotsworthTestBase):
    def setUp(self):
        super(TestLoginFlow, self).setUp()
        self.old_state_machine_states = pickle.dumps(state_machine._states)
        state_machine.register_state(AlwaysPoppingTestState)

    def tearDown(self):
        super(TestLoginFlow, self).tearDown()
        state_machine._states = pickle.loads(self.old_state_machine_states)

    def test_global_state_doesnt_trigger_not_correct_scan_data(self):
        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '{"not_session_id": "abc"}'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': DefaultStateStrings.DEFAULT_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

    def test_global_state_ignores_bad_json(self):
        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': 'herpaderp I\'m some json'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': DefaultStateStrings.DEFAULT_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_session_details')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._get_user_session_by_id')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_global_state_begins_login_flow(self, send_channel_data, get_session_by_id, send_session_details):
        timestamp = datetime_to_utc_timestamp_millis(datetime.utcnow())
        bot_dashboard_response = {
            'id': 'abc',
            'data': {'code_type': 'login', 'created_at': timestamp, 'code_id': 'xyz'},
            'bots': ['123'],
            'bot': '123',
            'expired': False
        }
        get_session_by_id.return_value = bot_dashboard_response

        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '{"session_id": "abc"}'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': LoginWithKikStrings.CONFIRMATION_MESSAGE,
            'suggestedResponses': ['Yes', 'No'],
            'typeTime': 0
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.LOGIN_WITH_KIK_CONFIRM])

        self.assertEqual(send_channel_data.call_count, 1)
        self.assertEqual(send_channel_data.call_args[0][0], 'xyz')
        self.assertEqual(send_channel_data.call_args[0][1], LoginWithKikChannelMessages.WAITING)

        self.assertEqual(get_session_by_id.call_args[0][0], 'abc')
        self.assertEqual(send_session_details.call_args[0][0], 'abc')

        bot_dashboard_response['data']['username'] = 'aleem'
        self.assertEqual(send_session_details.call_args[0][1], bot_dashboard_response['data'])

    def test_login_scan_data_bad_data_param(self):
        timestamp = datetime_to_utc_timestamp_millis(datetime.utcnow())
        bot_dashboard_response = {
            'id': 'abc',
            'data': {'code_type': 'login', 'created_at': timestamp, 'code_id': 'xyz'},
            'bots': ['123'],
            'expired': False
        }
        self.set_urlfetch_response(content=json.dumps(bot_dashboard_response))

        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '[{"session_id": "abc"}]'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': DefaultStateStrings.DEFAULT_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_login_scan_data_expired_session(self, send_channel_data):
        timestamp = datetime_to_utc_timestamp_millis(datetime.utcnow())
        bot_dashboard_response = {
            'id': 'abc',
            'data': {'code_type': 'login', 'created_at': timestamp, 'code_id': 'xyz'},
            'bots': ['123'],
            'expired': True
        }
        self.set_urlfetch_response(content=json.dumps(bot_dashboard_response))

        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '{"session_id": "abc"}'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': LoginWithKikStrings.EXPIRED_TOKEN_MESSAGE
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

        self.assertEqual(send_channel_data.call_count, 1)
        self.assertEqual(send_channel_data.call_args[0][0], 'xyz')
        self.assertEqual(send_channel_data.call_args[0][1], LoginWithKikChannelMessages.EXPIRED_KEY)

    def test_login_scan_data_session_not_found(self):
        self.set_urlfetch_response(status=404)

        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '{"session_id": "abc"}'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': LoginWithKikStrings.INVALID_TOKEN_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_login_scan_data_session_already_used(self, send_channel_data):
        timestamp = datetime_to_utc_timestamp_millis(datetime.utcnow())
        bot_dashboard_response = {
            'id': 'abc',
            'data': {'code_type': 'login', 'created_at': timestamp, 'code_id': 'xyz', 'username': 'aleem'},
            'bots': ['123'],
            'expired': False
        }
        self.set_urlfetch_response(content=json.dumps(bot_dashboard_response))

        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '{"session_id": "abc"}'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': LoginWithKikStrings.EXPIRED_TOKEN_MESSAGE
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

        self.assertEqual(send_channel_data.call_count, 1)
        self.assertEqual(send_channel_data.call_args[0][0], 'xyz')
        self.assertEqual(send_channel_data.call_args[0][1], LoginWithKikChannelMessages.EXPIRED_KEY)

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_session_details')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._get_user_session_by_id')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_login_scan_data_session_no_bots(self, send_channel_data, get_session_by_id, send_session_details):
        timestamp = datetime_to_utc_timestamp_millis(datetime.utcnow())
        bot_dashboard_response = {
            'id': 'abc',
            'data': {'code_type': 'login', 'created_at': timestamp, 'code_id': 'xyz'},
            'bots': [],
            'expired': False
        }
        get_session_by_id.return_value = bot_dashboard_response

        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '{"session_id": "abc"}'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': LoginWithKikStrings.NO_BOTS_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

        self.assertEqual(send_channel_data.call_count, 1)
        self.assertEqual(send_channel_data.call_args[0][0], 'xyz')
        self.assertEqual(send_channel_data.call_args[0][1], LoginWithKikChannelMessages.NO_BOTS)

        self.assertEqual(get_session_by_id.call_args[0][0], 'abc')
        self.assertEqual(send_session_details.call_args[0][0], 'abc')

        bot_dashboard_response['data']['username'] = 'aleem'
        self.assertEqual(send_session_details.call_args[0][1], bot_dashboard_response['data'])

    def test_login_scan_data_broken_kik_code(self):
        timestamp = datetime_to_utc_timestamp_millis(datetime.utcnow())
        bot_dashboard_response = {
            'id': 'abc',
            'data': {'created_at': timestamp, 'code_id': 'xyz'},
            'bots': [],
            'expired': False
        }
        self.set_urlfetch_response(content=json.dumps(bot_dashboard_response))

        incoming_message = {'from': 'aleem', 'type': MessageType.SCAN_DATA, 'data': '{"session_id": "abc"}'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': LoginWithKikStrings.INVALID_KIK_CODE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

    def test_on_resume_scan_state(self):
        BotUser(id='aleem', states=[StateTypes.DEFAULT, StateTypes.LINK_WITH_KIK_SCAN, 'pop-state']).put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'yo'}
        self.bot_call([incoming_message], [])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.DEFAULT])

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_session_details')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._get_user_session_by_id')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_confirm_state_positive_response(self, send_channel_data, get_session_by_id, send_session_details):
        BotUser(id='aleem', states=[StateTypes.LOGIN_WITH_KIK_CONFIRM]).put()
        UserSessionMap(id='aleem', session_id='abc', channel_token='xyz', last_bot_id='my_bot').put()

        get_session_by_id.return_value = {'data': {}}

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'yah'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': LoginWithKikStrings.SUCCESS_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

        self.assertEqual(send_channel_data.call_count, 1)
        self.assertEqual(send_channel_data.call_args[0][0], 'xyz')
        self.assertEqual(send_channel_data.call_args[0][1], {
            'status': LoginWithKikChannelMessages.LOGIN_SUCCESS,
            'send_tos_status': True,
            'session_id': 'abc'
        })

        self.assertEqual(get_session_by_id.call_args[0][0], 'abc')
        self.assertEqual(send_session_details.call_args[0][0], 'abc')
        self.assertEqual(send_session_details.call_args[0][1], {'bot': 'my_bot'})

        self.assertEqual(UserSessionMap.query().count(), 0)

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._get_user_session_by_id')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_confirm_state_positive_response_session_fetch_failed(self, send_channel_data, get_session_by_id):
        BotUser(id='aleem', states=[StateTypes.LOGIN_WITH_KIK_CONFIRM]).put()
        UserSessionMap(
            id='aleem',
            session_id='abc',
            channel_token='xyz',
            last_bot_id='my_bot',
            link_email='test_example@kik.com'
        ).put()

        get_session_by_id.side_effect = InvalidTokenError

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'yah'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': LoginWithKikStrings.INVALID_TOKEN_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

        self.assertEqual(send_channel_data.call_count, 0)
        self.assertEqual(get_session_by_id.call_args[0][0], 'abc')

        self.assertEqual(UserSessionMap.query().count(), 0)

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_session_details')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._get_user_session_by_id')
    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_confirm_state_positive_response_channel_failed(self, send_channel_data, get_session_by_id,
                                                            send_session_details):
        BotUser(id='aleem', states=[StateTypes.LOGIN_WITH_KIK_CONFIRM]).put()
        UserSessionMap(
            id='aleem',
            session_id='abc',
            channel_token='xyz',
            last_bot_id='my_bot',
            link_email='test_example@kik.com'
        ).put()

        get_session_by_id.return_value = {'data': {}}
        send_channel_data.side_effect = InvalidChannelError

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'yah'}
        outgoing_message = {'to': 'aleem', 'type': MessageType.TEXT, 'body': LoginWithKikStrings.CHANNEL_ERROR}
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

        self.assertEqual(send_session_details.call_count, 1)
        self.assertEqual(send_channel_data.call_count, 1)
        self.assertEqual(get_session_by_id.call_args[0][0], 'abc')

        self.assertEqual(UserSessionMap.query().count(), 0)

    @mock.patch('lib.session_requests_mixin.SessionRequestsMixin._send_channel_data')
    def test_confirm_state_negative_response(self, send_channel_data):
        BotUser(id='aleem', states=[StateTypes.LOGIN_WITH_KIK_CONFIRM]).put()
        UserSessionMap(id='aleem', session_id='abc', channel_token='xyz', last_bot_id='my_bot').put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'nah'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': LoginWithKikStrings.CANCELLED_MESSAGE
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [DefaultState.type()])

        self.assertEqual(send_channel_data.call_count, 1)
        self.assertEqual(send_channel_data.call_args[0][0], 'xyz')
        self.assertEqual(send_channel_data.call_args[0][1], LoginWithKikChannelMessages.LOGIN_TERMINATED)

        self.assertEqual(UserSessionMap.query().count(), 0)

    def test_confirm_state_unknown_response(self):
        BotUser(id='aleem', states=[StateTypes.LOGIN_WITH_KIK_CONFIRM]).put()
        UserSessionMap(id='aleem', session_id='abc', channel_token='xyz', last_bot_id='my_bot').put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'I like eating crayons.'}
        outgoing_message = {
            'to': 'aleem',
            'type': MessageType.TEXT,
            'body': LoginWithKikStrings.CONFUSED_MESSAGE,
            'suggestedResponses': ['Yes', 'No'],
            'typeTime': 0
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.LOGIN_WITH_KIK_CONFIRM])

        self.assertEqual(UserSessionMap.query().count(), 1)

    def test_on_resume_confirm_state(self):
        BotUser(id='aleem', states=[StateTypes.DEFAULT, StateTypes.LOGIN_WITH_KIK_CONFIRM, 'pop-state']).put()

        incoming_message = {'from': 'aleem', 'type': MessageType.TEXT, 'body': 'yo'}
        self.bot_call([incoming_message], [])

        user = BotUser.get_by_id('aleem')
        self.assertEqual(user.states, [StateTypes.DEFAULT])
