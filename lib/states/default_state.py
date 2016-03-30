from kik.messages.text import TextMessage
from lib.__init__ import get_kik_api
from lib.state_machine import State, Transition
from lib.states.state_types import StateTypes


class DefaultStateStrings(object):
    WELCOME_MESSAGE = 'Welcome, {first_name}!'


class DefaultState(State):

    @staticmethod
    def type():
        return StateTypes.DEFAULT

    def on_message(self, message):
        profile = get_kik_api().user.get(message.from_user)
        m = DefaultStateStrings.WELCOME_MESSAGE.format(first_name=profile['firstName'])
        return Transition([TextMessage(to=self.user.id, body=m)], StateTypes.MENU)
