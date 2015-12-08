from config import Config
from lib import logging
from lib.admin_requests_mixin import AdminRequestsMixin, AdminFetchError
from lib.kik_bot import make_text_message, get_user_info, UserInfoError
from lib.state_machine import State, LambdaTransition, StackTransition
from state_types import StateTypes
from secrets import BOTSWORTH_API_KEY


class DefaultStateStrings(object):
    DEFAULT_MESSAGE = 'I\'m sorry, I don\'t understand. Please refer to the instructions on the Bot Dashboard login page'  # noqa
    WELCOME_MESSAGE = 'Welcome back, {}'
    PROFILE_ERROR_MESSAGE = 'There was an error getting your profile'


class DefaultState(State, AdminRequestsMixin):
    @staticmethod
    def type():
        return StateTypes.DEFAULT

    def on_message(self, message):
        if self.user.id in Config.EARLY_ACCESS_WHITELIST:
            try:
                if self.user.bots():
                    user_info = get_user_info(self.user.id, Config.BOTSWORTH_USERNAME, BOTSWORTH_API_KEY)
                    message_text = DefaultStateStrings.WELCOME_MESSAGE.format(user_info['firstName'])
                    return StackTransition([make_text_message(message_text, self.user.id)], StateTypes.MENU)
            except UserInfoError as e:
                logging.error(e)
                return LambdaTransition([make_text_message(DefaultStateStrings.PROFILE_ERROR_MESSAGE, self.user.id)])
            except AdminFetchError as e:
                logging.error(e)
                return LambdaTransition([make_text_message(DefaultStateStrings.PROFILE_ERROR_MESSAGE, self.user.id)])

        return LambdaTransition([make_text_message(DefaultStateStrings.DEFAULT_MESSAGE, self.user.id)])
