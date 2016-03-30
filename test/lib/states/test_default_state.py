import mock

from kik.messages.keyboards import SuggestedResponseKeyboard
from kik.messages.responses import TextResponse
from kik.messages.text import TextMessage
from lib.states.default_state import DefaultState, DefaultStateStrings
from lib.states.menu_state import MenuState
from lib.states.state_types import StateTypes
from model.bot_user import BotUser
from test.bot_test_base import BotTestBase


class MenuStateTest(BotTestBase):

    def test_static(self):
        self.assertEqual(DefaultState.type(), StateTypes.DEFAULT)

    @mock.patch('kik.api.UserApi.get', return_value={'firstName': 'Rems'})
    def test_stack_not_existing_user(self, get_user_profile):
        incoming_message = TextMessage(from_user='remi', body='Hello are you from my school?')
        srs = [TextResponse(body=x) for x in ['Color', 'Do nothing']]
        outgoing_message = TextMessage(to='remi', body=DefaultStateStrings.WELCOME_MESSAGE.format(first_name='Rems'),
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])

    @mock.patch('kik.api.UserApi.get', return_value={'firstName': 'Rems'})
    def test_stack_existing_user(self, get_user_profile):
        BotUser(id='remi').put()

        incoming_message = TextMessage(from_user='remi', body='Hello are you from my school?')
        srs = [TextResponse(body=x) for x in ['Color', 'Do nothing']]
        outgoing_message = TextMessage(to='remi', body=DefaultStateStrings.WELCOME_MESSAGE.format(first_name='Rems'),
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])
