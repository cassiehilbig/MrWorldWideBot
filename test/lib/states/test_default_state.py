import mock

from test.example_bot_test_base import ExampleBotTestBase
from lib.states.menu_state import MenuState
from lib.states.default_state import DefaultState, DefaultStateStrings
from model import BotUser
from const import MessageType


class MenuStateTest(ExampleBotTestBase):

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

        self.assertEqual(BotUser.get_by_id('remi').states, [DefaultState.type(), MenuState.type()])

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

        self.assertEqual(BotUser.get_by_id('remi').states, [DefaultState.type(), MenuState.type()])
