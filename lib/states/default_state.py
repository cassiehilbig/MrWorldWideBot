from kik.api import get_user_profile
from kik.messages import make_text_message
from lib.state_machine import State, Transition
from kik.state_machine import State, Transition

from lib.states.state_types import StateTypes
from config import Config


class DefaultStateStrings(object):
    WELCOME_MESSAGE = 'Welcome, {first_name}!'


class DefaultState(State):

    @staticmethod
    def type():
        return StateTypes.DEFAULT

    def on_message(self, message):
        profile = get_user_profile(message['from'], bot_name=Config.BOT_USERNAME, bot_api_key=Config.BOT_API_KEY)
        m = DefaultStateStrings.WELCOME_MESSAGE.format(first_name=profile['firstName'])
        return Transition([make_text_message(self.user.id, m)], StateTypes.MENU)
