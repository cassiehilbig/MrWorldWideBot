from lib.state_machine import State, StackTransition
from kik.api import get_user_profile
from kik.messages import make_text_message
from config import Config
from secrets import BOT_API_KEY


class DefaultStateStrings(object):
    WELCOME_MESSAGE = 'Welcome, {first_name}!'


class DefaultState(State):

    @staticmethod
    def type():
        return 'default'

    def on_message(self, message):
        profile = get_user_profile(message['from'], bot_name=Config.BOT_USERNAME, bot_api_key=BOT_API_KEY)
        m = DefaultStateStrings.WELCOME_MESSAGE.format(first_name=profile['firstName'])
        return StackTransition([make_text_message(m, self.user.id)], 'menu')
