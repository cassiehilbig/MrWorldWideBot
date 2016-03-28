from kik.messages.text import TextMessage
from lib.state_machine import KeywordState, keyword_response, ConfirmationState, Transition, PopTransition,\
    LambdaTransition

from lib.states.state_types import StateTypes
from lib.message_types import MessageType


COLORS = ['White', 'Blue', 'Red', 'Purple', 'Orange']


class ChooseFavoriteColorStrings(object):

    UNKNOWN_MESSAGE_TYPE = 'Please send me your favorite color.'
    UNKNOWN_COLOR = 'I don\'t know this color :( Please pick from {}.'.format(', '.join(COLORS))
    CANCEL_MESSAGE = 'Okay no problem, you can choose one later.'
    CONFIRM_COLOR = 'So your favorite color is {color}?'
    CONFIRMED_COLOR = 'Okay, your favorite color is now {color}!'
    CONFIRMATION_CANCELLED = 'Okay, so what is your favorite color then?'
    CONFIRMATION_CONFUSED = 'So is your favorite color {color} or not?'


class ChooseColorState(KeywordState):

    @staticmethod
    def type():
        return StateTypes.CHOOSE_COLOR

    def __init__(self, user):
        super(ChooseColorState, self).__init__(user)

        # We don't want to have too many functions, so let's add suggested responses dynamically
        self.suggested_responses = COLORS + self.suggested_responses

    @keyword_response('Cancel', 'back')
    def handle_cancel(self, message):
        return PopTransition([TextMessage(to=self.user.id, body=ChooseFavoriteColorStrings.CANCEL_MESSAGE)])

    def handle_unmatched(self, message):
        if message['type'] != MessageType.TEXT:
            return LambdaTransition([TextMessage(to=self.user.id,
                                                 body=ChooseFavoriteColorStrings.UNKNOWN_MESSAGE_TYPE)])

        lower_colors = [c.lower() for c in COLORS]
        pick = message['body'].strip().lower()

        if pick not in lower_colors:
            return LambdaTransition([TextMessage(to=self.user.id, body=ChooseFavoriteColorStrings.UNKNOWN_COLOR)])

        self.user.get_state_data(ConfirmColorState.type())['color'] = pick

        message = ChooseFavoriteColorStrings.CONFIRM_COLOR.format(color=pick)
        return Transition([TextMessage(to=self.user.id, body=message)], ConfirmColorState.type())

    def on_resume(self):
        return LambdaTransition([TextMessage(to=self.user.id, body=ChooseFavoriteColorStrings.UNKNOWN_MESSAGE_TYPE)])


class ConfirmColorState(ConfirmationState):

    @staticmethod
    def type():
        return StateTypes.CONFIRM_COLOR

    def handle_positive_response(self, message):
        color = self.user.current_state_data()['color']

        self.user.clear_current_state_data()

        m = ChooseFavoriteColorStrings.CONFIRMED_COLOR.format(color=color)
        return PopTransition([TextMessage(to=self.user.id, body=m)])

    def handle_negative_response(self, message):
        self.user.clear_current_state_data()

        return Transition([
            TextMessage(to=self.user.id, body=ChooseFavoriteColorStrings.CONFIRMATION_CANCELLED)],
            ChooseColorState.type()
        )

    def handle_unmatched(self, message):
        color = self.user.current_state_data()['color']
        m = ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color=color)

        return LambdaTransition([TextMessage(to=self.user.id, body=m)])

    def on_resume(self):
        color = self.user.current_state_data()['color']
        m = ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color=color)

        return LambdaTransition([TextMessage(to=self.user.id, body=m)])
