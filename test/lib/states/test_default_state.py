import mock

from test.botsworth_test_base import BotsworthTestBase
from config import Config
from const import MessageType
from lib.admin_requests_mixin import AdminFetchError
from lib.kik_bot import UserInfoError
from lib.states import DefaultState
from lib.states.default import DefaultStateStrings
from lib.states.state_types import StateTypes
from model import BotUser


class DefaultStateTest(BotsworthTestBase):
    def test_static(self):
        self.assertEqual(DefaultState(None).type(), StateTypes.DEFAULT)

    def test_message(self):
        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'Yo are you botsworth from my school?'}
        outgoing_message = {'type': MessageType.TEXT, 'to': 'aleem', 'body': DefaultStateStrings.DEFAULT_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states, [DefaultState.type()])

    @mock.patch('lib.states.default.get_user_info')
    @mock.patch('lib.admin_requests_mixin.AdminRequestsMixin._get_admin')
    def test_message_early_access_user(self, get_admin, get_user_info):
        get_admin.return_value = {
            'bots': [{'id': 'msging_api_test1'}]
        }
        get_user_info.return_value = {
            'firstName': 'Some guy'
        }

        username = Config.EARLY_ACCESS_WHITELIST[0]
        incoming_message = {'type': MessageType.TEXT, 'from': username, 'body': 'Open seasame!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': username,
            'body': DefaultStateStrings.WELCOME_MESSAGE.format('Some guy'),
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(get_admin.call_count, 1)
        self.assertEqual(get_user_info.call_count, 1)

        self.assertEqual(BotUser.get_by_id(username).states, [DefaultState.type(), StateTypes.MENU])

    @mock.patch('lib.states.default.get_user_info')
    @mock.patch('lib.admin_requests_mixin.AdminRequestsMixin._get_admin')
    def test_message_early_access_user_no_bots(self, get_admin, get_user_info):
        get_admin.return_value = {
            'bots': []
        }

        username = Config.EARLY_ACCESS_WHITELIST[0]
        incoming_message = {'type': MessageType.TEXT, 'from': username, 'body': 'Yo are you botsworth from my school?'}
        outgoing_message = {'type': MessageType.TEXT, 'to': username, 'body': DefaultStateStrings.DEFAULT_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id(username).states, [DefaultState.type()])

    @mock.patch('lib.states.default.get_user_info', side_effect=UserInfoError)
    @mock.patch('lib.admin_requests_mixin.AdminRequestsMixin._get_admin', return_value={'bots': [{'id': 'a'}]})
    def test_message_early_access_user_info_error(self, get_admin, get_user_info):
        username = Config.EARLY_ACCESS_WHITELIST[0]
        incoming_message = {'type': MessageType.TEXT, 'from': username, 'body': 'Yo are you botsworth from my school?'}
        outgoing_message = {'type': MessageType.TEXT, 'to': username, 'body': DefaultStateStrings.PROFILE_ERROR_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id(username).states, [DefaultState.type()])

    @mock.patch('lib.states.default.get_user_info')
    @mock.patch('lib.admin_requests_mixin.AdminRequestsMixin._get_admin', side_effect=AdminFetchError)
    def test_message_early_access_admin_fetch_error(self, get_admin, get_user_info):
        username = Config.EARLY_ACCESS_WHITELIST[0]
        incoming_message = {'type': MessageType.TEXT, 'from': username, 'body': 'Yo are you botsworth from my school?'}
        outgoing_message = {'type': MessageType.TEXT, 'to': username, 'body': DefaultStateStrings.PROFILE_ERROR_MESSAGE}
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id(username).states, [DefaultState.type()])
