import pickle

import mock

from test.botsworth_test_base import BotsworthTestBase
from const import MessageType
from model import BotUser
from lib.botsworth_state_machine import state_machine
from lib.state_machine import State, PopTransition
from lib.states.menu.menu_state import MenuStateStrings, MenuState
from lib.states.state_types import StateTypes
from lib.states.create import ChooseUsernameState


class AlwaysPoppingTestState(State):
    @staticmethod
    def type():
        return 'pop-state'

    def on_message(self, message):
        return PopTransition([])


class MenuStateTest(BotsworthTestBase):
    def setUp(self):
        super(MenuStateTest, self).setUp()
        self.old_state_machine_states = pickle.dumps(state_machine._states)
        state_machine.register_state(AlwaysPoppingTestState)

    def tearDown(self):
        super(MenuStateTest, self).tearDown()
        state_machine._states = pickle.loads(self.old_state_machine_states)

    def test_static(self):
        self.assertEqual(MenuState(None).type(), StateTypes.MENU)

    def test_create_bot_response(self):
        BotUser(id='aleem', states=[StateTypes.MENU]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'I wanna create a bot, yo!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.CREATE_A_BOT,
            'suggestedResponses': ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('aleem').states, [MenuState.type(), ChooseUsernameState.type()])

    @mock.patch(
        'lib.admin_requests_mixin.AdminRequestsMixin._get_admin',
        return_value={'bots': [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]}
    )
    def test_set_profile_pic_response(self, get_admin):
        BotUser(id='aleem', states=[StateTypes.MENU]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'Change my pic up!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.UPDATE_PROFILE_PICTURE,
            'suggestedResponses': ['a', 'b', 'c', 'Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('aleem').states,
                         [StateTypes.MENU, StateTypes.UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT])

    @mock.patch(
        'lib.admin_requests_mixin.AdminRequestsMixin._get_admin',
        return_value={'bots': [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]}
    )
    def test_set_display_name_response(self, get_admin):
        user = BotUser(id='aleem', states=[StateTypes.MENU])
        user.put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'Change my name'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.UPDATE_DISPLAY_NAME,
            'suggestedResponses': ['a', 'b', 'c', 'Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('aleem').states,
                         [StateTypes.MENU, StateTypes.UPDATE_BOT_DISPLAY_NAME_SELECT_BOT])
        self.assertEqual(get_admin.call_count, 1)

    def test_docs_response(self):
        BotUser(id='aleem', states=[StateTypes.MENU]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'How do I use this bloody API?'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.DOCS_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('aleem').states, [StateTypes.MENU])

    def test_unknown_response(self):
        BotUser(id='aleem', states=[StateTypes.MENU]).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'My cabbages!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.UNKNOWN_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('aleem').states, [StateTypes.MENU])

    def test_resume_message(self):
        BotUser(id='aleem', states=[StateTypes.MENU, 'pop-state']).put()
        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'My cabbages!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.RESUME_RESPONSE,
            'suggestedResponses': ['Create a Bot', 'Set Profile Pic', 'Set Display Name', 'Docs']
        }
        self.bot_call([incoming_message], [outgoing_message])
        self.assertEqual(BotUser.get_by_id('aleem').states, [StateTypes.MENU])
