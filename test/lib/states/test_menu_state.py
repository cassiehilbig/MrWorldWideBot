from test.example_bot_test_base import ExampleBotTestBase
from lib.states.menu_state import MenuState, MenuStateStrings
from model import BotUser
from const import MessageType


class MenuStateTest(ExampleBotTestBase):

    def test_confused(self):
        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'Hello are you from my school?'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': MenuStateStrings.CONFUSED_MESSAGE,
            'suggestedResponses': ['Color', 'Do nothing']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states, [MenuState.type()])

    def test_color(self):
        incoming_message = {'type': MessageType.TEXT, 'from': 'aleem', 'body': 'Yo I wanna set my favorite color!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'aleem',
            'body': MenuStateStrings.COLOR_MESSAGE,
            'suggestedResponses': ['Color', 'Do nothing']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('aleem').states, [MenuState.type()])

    def test_resume(self):
        pass
