from test.example_bot_test_base import ExampleBotTestBase
from lib.state_machine import State
from lib.bot_state_machine import state_machine
from lib.states.picture .sent_picture_state import SentPictureStrings
from model import BotUser
from const import MessageType


class GenericState(State):

    @staticmethod
    def type():
        return 'foo'


class PictureStateTest(ExampleBotTestBase):

    def setUp(self):
        super(ExampleBotTestBase, self).setUp()
        self.old_states = state_machine._states
        state_machine.register_state(GenericState)

    def tearDown(self):
        super(ExampleBotTestBase, self).tearDown()
        state_machine._states = self.old_states

    def test_intercept(self):
        BotUser(id='remi', states=[GenericState.type()]).put()

        incoming_message = {'type': MessageType.PICTURE, 'from': 'remi', 'picUrl': 'http://yolo'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': SentPictureStrings.SENT_PICTURE_MESSAGE
        }

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [GenericState.type()])
