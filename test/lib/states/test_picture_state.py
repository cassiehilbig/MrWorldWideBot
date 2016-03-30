from kik.messages.picture import PictureMessage
from kik.messages.text import TextMessage
from lib.bot_state_machine import state_machine
from lib.states.generic_state import GenericState
from lib.states.picture.sent_picture_state import SentPictureStrings, SentPictureState
from lib.states.state_types import StateTypes
from model.bot_user import BotUser
from test.bot_test_base import BotTestBase


class PictureStateTest(BotTestBase):

    def setUp(self):
        super(BotTestBase, self).setUp()
        self.old_states = state_machine._states
        state_machine.register_state(GenericState)

    def tearDown(self):
        super(BotTestBase, self).tearDown()
        state_machine._states = self.old_states

    def test_static(self):
        self.assertEqual(SentPictureState.type(), StateTypes.SENT_PICTURE)

    def test_intercept(self):
        BotUser(id='remi', states=[GenericState.type()]).put()

        incoming_message = PictureMessage(from_user='remi', pic_url='http://yolo')
        outgoing_message = TextMessage(to='remi', body=SentPictureStrings.SENT_PICTURE_MESSAGE)

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [GenericState.type()])
