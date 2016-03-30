from kik.messages.keyboards import SuggestedResponseKeyboard
from kik.messages.responses import TextResponse
from kik.messages.scan_data import ScanDataMessage
from kik.messages.text import TextMessage
from lib.bot_state_machine import state_machine
from lib.states import DefaultState
from lib.states.always_popping_state import AlwaysPoppingState
from lib.states.color.choose_favorite_color_flow import ChooseFavoriteColorStrings, ChooseColorState,\
    ConfirmColorState, COLORS
from lib.states.generic_state import GenericState
from lib.states.state_types import StateTypes
from model.bot_user import BotUser
from test.bot_test_base import BotTestBase


class ChooseColorTest(BotTestBase):
    def test_static(self):
        self.assertEqual(ChooseColorState.type(), StateTypes.CHOOSE_COLOR)

    def test_confused(self):
        BotUser(id='remi', states=[ChooseColorState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='what is a color')
        srs = [TextResponse(body=c) for c in COLORS]
        srs.append(TextResponse(body='Cancel'))
        outgoing_message = TextMessage(to='remi', body=ChooseFavoriteColorStrings.UNKNOWN_COLOR,
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [ChooseColorState.type()])

    def test_unknown_type(self):
        BotUser(id='remi', states=[ChooseColorState.type()]).put()

        incoming_message = ScanDataMessage(from_user='remi', data='yolol')
        srs = [TextResponse(body=c) for c in COLORS]
        srs.append(TextResponse(body='Cancel'))
        outgoing_message = TextMessage(to='remi', body=ChooseFavoriteColorStrings.UNKNOWN_MESSAGE_TYPE,
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])
        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [ChooseColorState.type()])

    def test_cancel(self):
        BotUser(id='remi', states=[GenericState.type(), ChooseColorState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='cancel')
        outgoing_message = TextMessage(to='remi', body=ChooseFavoriteColorStrings.CANCEL_MESSAGE)

        self.bot_call([incoming_message], [outgoing_message])

        self.assertEqual(BotUser.get_by_id('remi').states, [GenericState.type()])

    def test_color(self):
        BotUser(id='remi', states=[GenericState.type(), ChooseColorState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='blue')
        srs = [TextResponse(body=x) for x in ('Yes', 'No')]
        outgoing_message = TextMessage(to='remi', body=ChooseFavoriteColorStrings.CONFIRM_COLOR.format(color='blue'),
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [GenericState.type(), ConfirmColorState.type()])
        self.assertEqual(user.state_data, {ConfirmColorState.type(): {'color': 'blue'}})

    def test_resume(self):
        BotUser(id='remi', states=[ChooseColorState.type(), AlwaysPoppingState.type()]).put()

        incoming_message = TextMessage(from_user='remi', body='yolo')
        srs = [TextResponse(body=c) for c in COLORS]
        srs.append(TextResponse(body='Cancel'))
        outgoing_message = TextMessage(to='remi', body=ChooseFavoriteColorStrings.UNKNOWN_MESSAGE_TYPE,
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [ChooseColorState.type()])


class ConfirmColorTest(BotTestBase):

    def setUp(self):
        super(BotTestBase, self).setUp()
        state_machine.register_state(DefaultState)
        state_machine.register_state(GenericState)
        state_machine.register_state(AlwaysPoppingState)

    def test_static(self):
        self.assertEqual(ConfirmColorState.type(), StateTypes.CONFIRM_COLOR)

    def test_confused(self):
        BotUser(id='remi',
                states=[ConfirmColorState.type()],
                state_data={ConfirmColorState.type(): {'color': 'blue'}}).put()

        incoming_message = TextMessage(from_user='remi', body='what did i do ?????')
        srs = [TextResponse(body=x) for x in ['Yes', 'No']]
        outgoing_message = TextMessage(to='remi',
                                       body=ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color='blue'),
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [ConfirmColorState.type()])
        self.assertEqual(user.state_data, {ConfirmColorState.type(): {'color': 'blue'}})

    def test_cancel(self):
        BotUser(id='remi',
                states=[ConfirmColorState.type()],
                state_data={ConfirmColorState.type(): {'color': 'blue'}}).put()

        incoming_message = TextMessage(from_user='remi', body='nope!')
        srs = [TextResponse(body=c) for c in COLORS]
        srs.append(TextResponse(body='Cancel'))
        outgoing_message = TextMessage(to='remi',
                                       body=ChooseFavoriteColorStrings.CONFIRMATION_CANCELLED.format(color='blue'),
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])
        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [ChooseColorState.type()])
        self.assertEqual(user.state_data, {})

    def test_confirm(self):
        BotUser(id='remi',
                states=[GenericState.type(), ConfirmColorState.type()],
                state_data={ConfirmColorState.type(): {'color': 'blue'}}).put()

        incoming_message = TextMessage(from_user='remi', body='sure!')
        outgoing_message = TextMessage(to='remi',
                                       body=ChooseFavoriteColorStrings.CONFIRMED_COLOR.format(color='blue'))

        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [GenericState.type()])
        self.assertEqual(user.state_data, {})

    def test_resume(self):
        BotUser(id='remi',
                states=[ConfirmColorState.type(), AlwaysPoppingState.type()],
                state_data={ConfirmColorState.type(): {'color': 'blue'}}).put()

        incoming_message = TextMessage(from_user='remi', body='yolo')
        srs = [TextResponse(body=x) for x in ['Yes', 'No']]
        outgoing_message = TextMessage(to='remi',
                                       body=ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color='blue'),
                                       keyboards=[SuggestedResponseKeyboard(to='remi', responses=srs)])

        self.bot_call([incoming_message], [outgoing_message])

        user = BotUser.get_by_id('remi')
        self.assertEqual(user.states, [ConfirmColorState.type()])
        self.assertEqual(user.state_data, {ConfirmColorState.type(): {'color': 'blue'}})
