import re

from lib.kik_bot import make_text_message
from lib.state_machine import KeywordState, keyword_response, PopTransition, LambdaTransition, ConfirmationState,\
    Transition, StackTransition
from lib.admin_requests_mixin import AdminRequestsMixin, UsernameAvailableCheckError, CreateBotError
from lib.states.state_types import StateTypes
from lib import logging
from const import MessageType, BOT_ID_REGEX


class CreateBotStrings(object):
    CONFIRM_MESSAGE = 'This will create a new bot named "{}". Is this correct?'
    CONFUSED_MESSAGE = 'I\'m sorry. I didn\'t understand that. What would you like your bot\'s username to be?'
    UNAVAILABLE_MESSAGE = 'I\'m sorry, "{}" is not an available username. Please choose another one'
    INVALID_USERNAME_MESSAGE = 'I\'m sorry, that is not a valid username. Please choose another one'
    NEGATIVE_CONFIRMATION_MESSAGE = 'Okay, what would you like your bot username to be?'
    CONFIRMATION_CONFUSED_MESSAGE = 'I\'m sorry, I did not understand that. Would you like your bot username to be "{}"?'  # noqa
    ERROR_CHECKING_AVAILABILITY_MESSAGE = 'I\'m sorry, there was an error checking for the username availability. Please try again'  # noqa
    BOT_CREATED_MESSAGE = 'Your bot was created! Its username is "{}". What may I help you with?'
    CREATE_BOT_ERROR_RETRY_MESSAGE = 'I\'m sorry, there was an error while creating your bot. Would you like to try again?'  # noqa

    MORE_SETUP_MESSAGE = 'Would you like to make more changes to your bot?'
    MORE_SETUP_BACK_MESSAGE = 'Alright, you can always do it later'
    SET_PICTURE_MESSAGE = 'Which picture would you like to use?'
    SET_DISPLAY_NAME_MESSAGE = 'Which display name would you like to use?'
    MORE_SETUP_CONFUSED_MESSAGE = 'I\'m sorry, I didn\'t understand that. What may I help you with?'


class ChooseUsernameState(KeywordState, AdminRequestsMixin):

    @staticmethod
    def type():
        return StateTypes.CREATE_BOT_USERNAME_SELECT

    @keyword_response('Cancel', 'back', 'no', 'abort')
    def handle_cancel(self, message):
        return PopTransition([])

    def handle_unmatched(self, message):
        if message['type'] != MessageType.TEXT:
            return LambdaTransition([make_text_message(CreateBotStrings.CONFUSED_MESSAGE, self.user.id)])

        # Format
        bot_id = message['body'].strip().lower()
        if not re.match(BOT_ID_REGEX, bot_id):
            return LambdaTransition([make_text_message(CreateBotStrings.INVALID_USERNAME_MESSAGE, self.user.id)])

        # Checking availability (before confirmation)
        try:
            availability_check = self._check_username_available(bot_id)
        except UsernameAvailableCheckError as e:
            logging.error(e)
            return LambdaTransition([make_text_message(CreateBotStrings.ERROR_CHECKING_AVAILABILITY_MESSAGE,
                                                       self.user.id)])

        if not availability_check.get('available'):
            message = CreateBotStrings.UNAVAILABLE_MESSAGE.format(bot_id)
            return LambdaTransition([make_text_message(message, self.user.id)])

        self.user.get_state_data(ConfirmUsernameState.type())['bot-username'] = bot_id

        message = CreateBotStrings.CONFIRM_MESSAGE.format(bot_id)
        return Transition([make_text_message(message, self.user.id)], ConfirmUsernameState.type())


class ConfirmUsernameState(ConfirmationState, AdminRequestsMixin):

    @staticmethod
    def type():
        return StateTypes.CREATE_BOT_USERNAME_CONFIRM

    def handle_positive_response(self, message):
        bot_username = self.user.current_state_data()['bot-username']
        try:
            self._create_bot(username=self.user.id, bot_id=bot_username, display_name=bot_username)
        except CreateBotError as e:
            logging.error(e)
            return LambdaTransition([make_text_message(CreateBotStrings.CREATE_BOT_ERROR_RETRY_MESSAGE, self.user.id)])

        message = CreateBotStrings.BOT_CREATED_MESSAGE.format(bot_username)

        self.user.get_state_data(MoreSetupState.type())['bot-username'] = bot_username
        self.user.clear_current_state_data()

        return Transition([make_text_message(message, self.user.id)], MoreSetupState.type())

    def handle_negative_response(self, message):
        self.user.clear_current_state_data()

        return Transition([make_text_message(CreateBotStrings.NEGATIVE_CONFIRMATION_MESSAGE, self.user.id)],
                          ChooseUsernameState.type())

    def handle_unmatched(self, message):
        bot_username = self.user.current_state_data()['bot-username']
        message = CreateBotStrings.CONFIRMATION_CONFUSED_MESSAGE.format(bot_username)
        return LambdaTransition([make_text_message(message, self.user.id)])


class MoreSetupState(KeywordState):

    @staticmethod
    def type():
        return StateTypes.CREATE_BOT_MORE_OPTIONS

    @keyword_response('Set profile picture', 'profile', 'pic', 'picture', 'photo')
    def handle_picture_message(self, message):
        bot_username = self.user.current_state_data()['bot-username']
        self.user.get_state_data(StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT)['bot-username'] = bot_username
        return StackTransition(
            [make_text_message(CreateBotStrings.SET_PICTURE_MESSAGE, self.user.id, suggested_responses=['Back'])],
            StateTypes.UPDATE_BOT_PROFILE_PICTURE_INPUT
        )

    @keyword_response('Set display name', 'display', 'name')
    def handle_display_name_message(self, message):
        bot_username = self.user.current_state_data()['bot-username']
        self.user.get_state_data(StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT)['bot-username'] = bot_username
        return StackTransition(
            [make_text_message(CreateBotStrings.SET_DISPLAY_NAME_MESSAGE, self.user.id, suggested_responses=['Back'])],
            StateTypes.UPDATE_BOT_DISPLAY_NAME_INPUT
        )

    @keyword_response('Menu', 'cancel', 'back', 'return')
    def handle_menu_message(self, message):
        self.user.clear_current_state_data()
        return PopTransition([make_text_message(CreateBotStrings.MORE_SETUP_BACK_MESSAGE, self.user.id)])

    def handle_unmatched(self, message):
        return LambdaTransition([make_text_message(CreateBotStrings.MORE_SETUP_CONFUSED_MESSAGE, self.user.id)])

    def on_resume(self):
        return LambdaTransition([make_text_message(CreateBotStrings.MORE_SETUP_MESSAGE, self.user.id)])
