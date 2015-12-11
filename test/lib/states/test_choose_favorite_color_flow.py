from test.example_bot_test_base import ExampleBotTestBase
from lib.states.color.choose_favorite_color_flow import ChooseFavoriteColorStrings, ChooseColorState,\
    ConfirmColorState, COLORS
from lib.state_machine import State
from lib.bot_state_machine import state_machine
from model import BotUser
from const import MessageType


class GenericState(State):

    @staticmethod
    def type():
        return 'foo'


class ChooseColorTest(ExampleBotTestBase):

    def setUp(self):
        super(ExampleBotTestBase, self).setUp()
        self.old_states = state_machine._states
        state_machine.register_state(GenericState)

    def tearDown(self):
        super(ExampleBotTestBase, self).tearDown()
        state_machine._states = self.old_states

    def test_confused(self):
        BotUser(id='remi', states=[ChooseColorState.type()]).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'what is a color'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': ChooseFavoriteColorStrings.UNKNOWN_COLOR,
            'suggestedResponses': COLORS + ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [ChooseColorState.type()])

    def test_unkown_type(self):
        BotUser(id='remi', states=[ChooseColorState.type()]).put()

        incoming_message = {'type': MessageType.PICTURE, 'from': 'remi', 'picUrl': 'http://yolo'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': ChooseFavoriteColorStrings.UNKNOWN_MESSAGE_TYPE,
            'suggestedResponses': COLORS + ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [ChooseColorState.type()])

    def test_cancel(self):
        BotUser(id='remi', states=[GenericState.type(), ChooseColorState.type()]).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'cancel'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': ChooseFavoriteColorStrings.CANCEL_MESSAGE
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [GenericState.type()])

    def test_color(self):
        BotUser(id='remi', states=[GenericState.type(), ChooseColorState.type()]).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'blue'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': ChooseFavoriteColorStrings.CONFIRM_COLOR.format(color='blue'),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [GenericState.type(), ConfirmColorState.type()])
        self.assertEqual(user.state_data, {ConfirmColorState.type(): {'color': 'blue'}})


class ConfirmColorTest(ExampleBotTestBase):

    def setUp(self):
        super(ExampleBotTestBase, self).setUp()
        self.old_states = state_machine._states
        state_machine.register_state(GenericState)

    def tearDown(self):
        super(ExampleBotTestBase, self).tearDown()
        state_machine._states = self.old_states

    def test_confused(self):
        BotUser(id='remi',
                states=[ConfirmColorState.type()],
                state_data={ConfirmColorState.type(): {'color': 'blue'}}).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'what did i do ?????'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color='blue'),
            'suggestedResponses': ['Yes', 'No']
        }
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [ConfirmColorState.type()])

    def test_cancel(self):
        BotUser(id='remi',
                states=[ConfirmColorState.type()],
                state_data={ConfirmColorState.type(): {'color': 'blue'}}).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'nope!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': ChooseFavoriteColorStrings.CONFIRMATION_CANCELLED.format(color='blue'),
            'suggestedResponses': COLORS + ['Cancel']
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [ChooseColorState.type()])
        self.assertEqual(user.state_data, {})

    def test_confirm(self):
        BotUser(id='remi',
                states=[GenericState.type(), ConfirmColorState.type()],
                state_data={ConfirmColorState.type(): {'color': 'blue'}}).put()

        incoming_message = {'type': MessageType.TEXT, 'from': 'remi', 'body': 'sure!'}
        outgoing_message = {
            'type': MessageType.TEXT,
            'to': 'remi',
            'body': ChooseFavoriteColorStrings.CONFIRMED_COLOR.format(color='blue')
        }
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [GenericState.type()])
        self.assertEqual(user.state_data, {})
