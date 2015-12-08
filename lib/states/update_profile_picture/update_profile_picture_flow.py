from const import MessageType
from lib.kik_bot import make_text_message
from lib.state_machine import KeywordState, keyword_response, Transition, PopTransition, LambdaTransition, \
    ConfirmationState
from lib.states.select_bot_name_state import SelectBotNameState, SelectBotNameStateStrings
from lib.states.state_types import StateTypes
from lib.admin_requests_mixin import AdminRequestsMixin, UpdateProfilePictureError
from lib import logging


class UpdateProfilePictureStateStrings(SelectBotNameStateStrings):
    SELECTED_BOT_NAME = 'What would you like to set {}\'s profile picture to be?'
    PROFILE_PICTURE_UPDATE_ERROR = 'I\'m sorry, an error occurred setting your profile picture. Please try again'
    PROFILE_PICTURE_UPDATE_SUCCESS = '{}\'s profile picture has been changed! You might have to restart Kik to see the change'  # noqa
    PROFILE_PICTURE_INVALID_MESSAGE_TYPE = 'I\'m sorry, I don\'t understand that message. Please send a picture message'
    PROFILE_PICTURE_CONFIRMATION_MESSAGE = 'Are you sure you want to update {}\'s profile picture to that image?'
    PROFILE_PICTURE_REPLACEMENT_MESSAGE = 'Ok then. What do you want {}\'s profile picture to be?'
    PROFILE_PICTURE_CONFIRMATION_UNKNOWN_MESSAGE = 'Are you sure you want to update {}\'s profile picture? Answer with "Yes" or "No"'  # noqa


class SelectBotUpdateProfilePictureState(SelectBotNameState):
    @staticmethod
    def type():
        return StateTypes.UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT

    def __init__(self, *args, **kwargs):
        super(SelectBotUpdateProfilePictureState, self).__init__(*args, **kwargs)
        self.suggested_responses = self.get_suggested_responses()

    def on_bot_name_message(self, message):
        self.user.get_state_data(UpdateProfilePictureState.type())['bot-username'] = message['body'].strip().lower()
        self.user.clear_current_state_data()
        return Transition([make_text_message(
            UpdateProfilePictureStateStrings.SELECTED_BOT_NAME.format(message['body']), self.user.id
        )], UpdateProfilePictureState.type())


class UpdateProfilePictureState(KeywordState, AdminRequestsMixin):
    @staticmethod
    def type():
        return StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT

    @keyword_response('Cancel', 'abort', 'quit', 'no')
    def handle_cancel_message(self, message):
        return PopTransition([])

    def handle_unmatched(self, message):
        if message['type'] == MessageType.PICTURE:
            confirm_state_data = self.user.get_state_data(UpdateProfilePictureConfirmationState.type())
            confirm_state_data['bot-username'] = self.user.current_state_data()['bot-username']
            confirm_state_data['profile-picture-url'] = message['picUrl']
            self.user.clear_current_state_data()
            return Transition(
                [make_text_message(UpdateProfilePictureStateStrings.PROFILE_PICTURE_CONFIRMATION_MESSAGE.format(
                    confirm_state_data['bot-username']
                ), self.user.id)],
                UpdateProfilePictureConfirmationState.type()
            )
        else:
            return LambdaTransition(
                [make_text_message(UpdateProfilePictureStateStrings.PROFILE_PICTURE_INVALID_MESSAGE_TYPE, self.user.id)]
            )


class UpdateProfilePictureConfirmationState(ConfirmationState, AdminRequestsMixin):
    @staticmethod
    def type():
        return StateTypes.UPDATE_BOT_PROFILE_PICTURE_CONFIRM

    def handle_positive_response(self, message):
        bot_selection_state = self.user.current_state_data()
        try:
            self._update_bot_profile_picture(
                self.user.id, bot_selection_state['bot-username'], bot_selection_state['profile-picture-url']
            )
        except UpdateProfilePictureError as e:
            logging.error(e)
            return LambdaTransition(
                [make_text_message(UpdateProfilePictureStateStrings.PROFILE_PICTURE_UPDATE_ERROR, self.user.id)]
            )

        self.user.clear_current_state_data()
        return PopTransition(
            [make_text_message(
                UpdateProfilePictureStateStrings.PROFILE_PICTURE_UPDATE_SUCCESS.format(
                    bot_selection_state['bot-username']
                ),
                self.user.id
            )]
        )

    def handle_negative_response(self, message):
        bot_selection_state = self.user.current_state_data()
        self.user.get_state_data(UpdateProfilePictureState.type())['bot-username'] = bot_selection_state['bot-username']
        self.user.clear_current_state_data()
        return Transition([
            make_text_message(
                UpdateProfilePictureStateStrings.PROFILE_PICTURE_REPLACEMENT_MESSAGE.format(
                    bot_selection_state['bot-username']
                ),
                self.user.id
            )
        ], UpdateProfilePictureState.type())

    def handle_unmatched(self, message):
        bot_selection_state = self.user.current_state_data()
        return LambdaTransition([
            make_text_message(UpdateProfilePictureStateStrings.PROFILE_PICTURE_CONFIRMATION_UNKNOWN_MESSAGE.format(
                bot_selection_state['bot-username']
            ), self.user.id)
        ])
