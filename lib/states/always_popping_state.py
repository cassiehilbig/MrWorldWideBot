from lib.state_machine import State, PopTransition
from lib.states.state_types import StateTypes


class AlwaysPoppingState(State):

    @staticmethod
    def type():
        return StateTypes.ALWAYS_POPPING

    def on_message(self, message):
        return PopTransition([])
