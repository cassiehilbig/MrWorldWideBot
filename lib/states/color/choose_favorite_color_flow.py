from lib.state_machine import KeywordState, keyword_response, ConfirmationState, Transition, PopTransition,\
    LambdaTransition
from lib.kik_bot import make_text_message
from const import MessageType


COLORS = ['White', 'Blue', 'Red', 'Purple', 'Orange']


class ChooseFavoriteColorStrings(object):

    UNKNOWN_MESSAGE_TYPE = 'Please send me your favorite color.'
    UNKNOWN_COLOR = 'I don\'t know this color :( Please pick from {}'.format(', '.join(COLORS))
    CANCEL_MESSAGE = 'Okay no problem, you can choose one later.'
    CONFIRM_COLOR = 'So your favorite color is {color}?'
    CONFIRMED_COLOR = 'Okay, your favorite color is now {color}!'
    CANCELLED_COLOR = 'Okay, so what is your favorite color then?'
    CONFIRMATION_CONFUSED = 'So is your favorite color {color} or not?'


class ChooseColorState(KeywordState):

    @staticmethod
    def type():
        return 'choose-color'

    @keyword_response('Cancel', 'back')
    def handle_cancel(self, message):
        return PopTransition([make_text_message(self.user.id, ChooseFavoriteColorStrings.CANCEL_MESSAGE)])

    def handle_unmatched(self, message):
        if message['type'] != MessageType.TEXT:
            return LambdaTransition([make_text_message(self.user.id, ChooseFavoriteColorStrings.UNKNOWN_MESSAGE_TYPE)])

        lower_colors = [c.lower() for c in COLORS]
        pick = message['body'].strip().lower()

        if pick not in lower_colors:
            return LambdaTransition([make_text_message(self.user.id, ChooseFavoriteColorStrings.UNKNOWN_COLOR)])

        self.user.get_state_data(ConfirmColorState.type())['color'] = pick

        message = ChooseFavoriteColorStrings.CONFIRM_COLOR.format(color=pick)
        return Transition([make_text_message(self.user.id, message)], ConfirmColorState.type())


class ConfirmColorState(ConfirmationState):

    @staticmethod
    def type():
        return 'confirm-color'

    def handle_positive_response(self, message):
        color = self.user.current_state_date()['color']

        self.user.clear_current_state_data()

        m = ChooseFavoriteColorStrings.CONFIRMED_COLOR.format(color=color)
        return PopTransition([make_text_message(self.user.id, m)])

    def handle_negative_response(self, message):
        self.user.clear_current_state_data()

        return Transition([make_text_message(self.user.id, message)], ChooseColorState.type())

    def handle_unmatched(self, message):
        color = self.user.current_state_data()['color']
        m = ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color=color)

        return LambdaTransition([make_text_message(self.user.id, m)])
