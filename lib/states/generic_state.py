from lib.state_machine import State
from lib.states.state_types import StateTypes


class GenericState(State):

    @staticmethod
    def type():
        return StateTypes.GENERIC
