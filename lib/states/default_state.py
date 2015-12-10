from lib.state_machine import State, StackTransition
from lib.kik_bot import make_text_message, get_user_profile
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
        return StackTransition([make_text_message(m)], 'menu')

