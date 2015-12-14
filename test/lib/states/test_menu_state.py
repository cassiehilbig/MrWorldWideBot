from kik.messages import MessageType

from test.example_bot_test_base import ExampleBotTestBase
from lib.states.menu_state import MenuState, MenuStateStrings
from lib.states.color.choose_favorite_color_flow import ChooseColorState, COLORS
from lib.state_machine import State, PopTransition
from lib.bot_state_machine import state_machine
from lib.states.state_types import StateTypes
from model import BotUser


class AlwaysPoppingState(State):

    @staticmethod
    def type():
        return 'pop'

    def on_message(self, message):
        return PopTransition([])


class MenuStateTest(ExampleBotTestBase):

    def setUp(self):
        super(ExampleBotTestBase, self).setUp()
        self.old_states = state_machine._states
        state_machine.register_state(AlwaysPoppingState)

    def tearDown(self):
        super(ExampleBotTestBase, self).tearDown()
        state_machine._states = self.old_states

    def test_static(self):
        self.assertEqual(MenuState.type(), StateTypes.MENU)

    def test_confused(self):
        BotUser(id='remi', states=[MenuState.type()]).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'Hello are you from my school?'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': MenuStateStrings.CONFUSED_MESSAGE,
            'suggestedResponses': ['Color', 'Do nothing']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])

    def test_color(self):
        BotUser(id='remi', states=[MenuState.type()]).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'Yo I wanna set my favorite color!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': MenuStateStrings.COLOR_MESSAGE,
            'suggestedResponses': COLORS + ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type(), ChooseColorState.type()])

    def test_resume(self):
        BotUser(id='remi', states=[MenuState.type(), AlwaysPoppingState.type()]).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'pop!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': MenuStateStrings.RESUME_MESSAGE,
            'suggestedResponses': ['Color', 'Do nothing']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])

    def test_nothing(self):
        BotUser(id='remi', states=[MenuState.type()]).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'do nothing'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': MenuStateStrings.NOTHING_MESSAGE,
            'suggestedResponses': ['Color', 'Do nothing']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [MenuState.type()])
