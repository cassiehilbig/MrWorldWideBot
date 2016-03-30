from kik.messages.keyboards import SuggestedResponseKeyboard
from kik.messages.responses import TextResponse
from kik.messages.text import TextMessage
from lib.bot_state_machine import state_machine
from lib.states.always_popping_state import AlwaysPoppingState
from lib.states.color.choose_favorite_color_flow import ChooseColorState, COLORS
from lib.states.menu_state import MenuState, MenuStateStrings
from lib.states.state_types import StateTypes
from model.bot_user import BotUser
from test.bot_test_base import BotTestBase


class MenuStateTest(BotTestBase):

    def setUp(self):
        super(BotTestBase, self).setUp()
        self.old_states = state_machine._states
        state_machine.register_state(AlwaysPoppingState)

    def tearDown(self):
        super(BotTestBase, self).tearDown()
        state_machine._states = self.old_states

    def test_static(self):
        self.assertEqual(MenuState.type(), StateTypes.MENU)

    def test_confused(self):
        BotUser(id='remi', states=[MenuState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='Hello are you from my school?')
        srs = [TextResponse(body=x) for x in ['Color', 'Do nothing']]
        outgoing_message = TextMessage(to='remi', body=MenuStateStrings.CONFUSED_MESSAGE,
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])

    def test_color(self):
        BotUser(id='remi', states=[MenuState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='Yo I wanna set my favourite colour')
        srs = [TextResponse(body=x) for x in COLORS]
        srs.append(TextResponse(body='Cancel'))
        outgoing_message = TextMessage(to='remi', body=MenuStateStrings.COLOR_MESSAGE,
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type(), ChooseColorState.type()])

    def test_resume(self):
        BotUser(id='remi', states=[MenuState.type(), AlwaysPoppingState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='pop!')
        srs = [TextResponse(body=x) for x in ['Color', 'Do nothing']]
        outgoing_message = TextMessage(to='remi', body=MenuStateStrings.RESUME_MESSAGE,
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])

    def test_nothing(self):
        BotUser(id='remi', states=[MenuState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='do nothing')
        srs = [TextResponse(body=x) for x in ['Color', 'Do nothing']]
        outgoing_message = TextMessage(to='remi', body=MenuStateStrings.NOTHING_MESSAGE,
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])
