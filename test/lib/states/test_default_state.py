import mock

from kik.messages import MessageType

from test.example_bot_test_base import ExampleBotTestBase
from lib.states.default_state import DefaultState, DefaultStateStrings
from lib.states.menu_state import MenuState
from lib.states.state_types import StateTypes
from model import BotUser


class MenuStateTest(ExampleBotTestBase):

    def test_static(self):
        self.assertEqual(DefaultState.type(), StateTypes.DEFAULT)

    @mock.patch('lib.states.default_state.get_user_profile', return_value={'firstName': 'Rems'})
    def test_stack_not_existing_user(self, get_user_profile):
        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'Hello are you from my school?'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': DefaultStateStrings.WELCOME_MESSAGE.format(first_name='Rems'),
            'suggestedResponses': ['Color', 'Do nothing']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])

    @mock.patch('lib.states.default_state.get_user_profile', return_value={'firstName': 'Rems'})
    def test_stack_existing_user(self, get_user_profile):
        BotUser(id='remi').put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'Hello are you from my school?'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': DefaultStateStrings.WELCOME_MESSAGE.format(first_name='Rems'),
            'suggestedResponses': ['Color', 'Do nothing']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])
