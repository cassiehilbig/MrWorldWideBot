from kik.messages import TextMessage

from app import kik
from lib.state_machine import State, Transition
from lib.states.state_types import StateTypes


class DefaultStateStrings(object):
    WELCOME_MESSAGE = 'Welcome to my hood, {first_name}! To get started, choose a language to translate to. If you want to switch languages later, tap "Choose Language"'


class DefaultState(State):
    @staticmethod
    def type():
        return StateTypes.DEFAULT

    def on_message(self, message):
        profile = kik.get_user(message.from_user)
        m = DefaultStateStrings.WELCOME_MESSAGE.format(first_name=profile.first_name)
        return Transition([TextMessage(to=self.user.id, body=m)], StateTypes.MENU)
