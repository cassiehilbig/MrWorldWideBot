import re

from const import DISPLAY_NAME_REGEX, MessageType
from lib.kik_bot import make_text_message
from lib.state_machine import KeywordState, keyword_response, Transition, PopTransition, LambdaTransition, \
    ConfirmationState
from lib.states.select_bot_name_state import SelectBotNameState, SelectBotNameStateStrings
from lib.states.state_types import StateTypes
from lib.admin_requests_mixin import AdminRequestsMixin, UpdateDisplayNameError
from lib import logging


class UpdateDisplayNameStateStrings(SelectBotNameStateStrings):
    SELECTED_BOT_NAME = 'What would you like {}\'s display name to be?'
    DISPLAY_NAME_UPDATE_ERROR = 'I\'m sorry, an error occurred setting your display name. Please try again'
    DISPLAY_NAME_BAD_INPUT = 'I\'m sorry, that\'s not a valid Display Name. They must be 1-32 characters in length. Please try again'  # noqa
    DISPLAY_NAME_UPDATE_SUCCESS = u'{}\'s display name has been changed to "{}". You might have to restart Kik to see the change'  # noqa
    DISPLAY_NAME_INVALID_MESSAGE_TYPE = 'I\'m sorry, I don\'t understand that message. Please send a text message'
    DISPLAY_NAME_CONFIRMATION_MESSAGE = u'Are you sure you want {}\'s display name to be "{}"?'
    DISPLAY_NAME_REPLACEMENT_MESSAGE = 'Ok then. What do you want {}\'s display name to be?'
    DISPLAY_NAME_CONFIRMATION_UNKNOWN_MESSAGE = u'Are you sure you want {}\'s display name to be "{}"? Answer with "Yes" or "No"'  # noqa


class SelectBotUpdateDisplayNameState(SelectBotNameState):
    @staticmethod
    def type():
        return StateTypes.UPDATE_BOT_DISPLAY_NAME_SELECT_BOT

    def __init__(self, *args, **kwargs):
        super(SelectBotUpdateDisplayNameState, self).__init__(*args, **kwargs)
        self.suggested_responses = self.get_suggested_responses()

    def on_bot_name_message(self, message):
        self.user.get_state_data(UpdateDisplayNameState.type())['bot-username'] = message['body'].strip().lower()
        self.user.clear_current_state_data()
        return Transition([make_text_message(
            UpdateDisplayNameStateStrings.SELECTED_BOT_NAME.format(message['body']), self.user.id
        )], UpdateDisplayNameState.type())


class UpdateDisplayNameState(KeywordState, AdminRequestsMixin):
    @staticmethod
    def type():
        return StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT

    @keyword_response('Cancel', 'abort', 'quit', 'no')
    def handle_cancel_message(self, message):
        return PopTransition([])

    def handle_unmatched(self, message):
        if message['type'] == MessageType.TEXT:
            if not re.match(DISPLAY_NAME_REGEX, message['body'].strip()):
                return LambdaTransition(
                    [make_text_message(UpdateDisplayNameStateStrings.DISPLAY_NAME_BAD_INPUT, self.user.id)]
                )

            confirm_state_data = self.user.get_state_data(UpdateDisplayNameConfirmationState.type())
            confirm_state_data['bot-username'] = self.user.current_state_data()['bot-username']
            confirm_state_data['display-name'] = message['body'].strip()
            self.user.clear_current_state_data()
            return Transition(
                [make_text_message(UpdateDisplayNameStateStrings.DISPLAY_NAME_CONFIRMATION_MESSAGE.format(
                    confirm_state_data['bot-username'], confirm_state_data['display-name']
                ), self.user.id)],
                UpdateDisplayNameConfirmationState.type()
            )
        else:
            return LambdaTransition(
                [make_text_message(UpdateDisplayNameStateStrings.DISPLAY_NAME_INVALID_MESSAGE_TYPE, self.user.id)]
            )


class UpdateDisplayNameConfirmationState(ConfirmationState, AdminRequestsMixin):
    @staticmethod
    def type():
        return StateTypes.UPDATE_BOT_DISPLAY_NAME_CONFIRM

    def handle_positive_response(self, message):
        bot_selection_state = self.user.current_state_data()
        try:
            self._update_bot_display_name(
                self.user.id, bot_selection_state['bot-username'], bot_selection_state['display-name']
            )
        except UpdateDisplayNameError as e:
            logging.error(e)
            return LambdaTransition(
                [make_text_message(UpdateDisplayNameStateStrings.DISPLAY_NAME_UPDATE_ERROR, self.user.id)]
            )

        self.user.clear_current_state_data()
        return PopTransition(
            [make_text_message(
                UpdateDisplayNameStateStrings.DISPLAY_NAME_UPDATE_SUCCESS.format(
                    bot_selection_state['bot-username'],
                    bot_selection_state['display-name']
                ),
                self.user.id
            )]
        )

    def handle_negative_response(self, message):
        bot_selection_state = self.user.current_state_data()
        self.user.get_state_data(UpdateDisplayNameState.type())['bot-username'] = bot_selection_state['bot-username']
        self.user.clear_current_state_data()
        return Transition([
            make_text_message(
                UpdateDisplayNameStateStrings.DISPLAY_NAME_REPLACEMENT_MESSAGE.format(
                    bot_selection_state['bot-username']
                ),
                self.user.id
            )
        ], UpdateDisplayNameState.type())

    def handle_unmatched(self, message):
        bot_selection_state = self.user.current_state_data()
        return LambdaTransition([
            make_text_message(UpdateDisplayNameStateStrings.DISPLAY_NAME_CONFIRMATION_UNKNOWN_MESSAGE.format(
                bot_selection_state['bot-username'],
                bot_selection_state['display-name']
            ), self.user.id)
        ])
