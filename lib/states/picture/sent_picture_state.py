from kik.messages import make_text_message
from kik.state_machine import State, PopTransition

from lib.states.state_types import StateTypes


class SentPictureStrings(object):

    SENT_PICTURE_MESSAGE = 'Oh that\'s a cute picture!'


class SentPictureState(State):

    @staticmethod
    def type():
        return StateTypes.SENT_PICTURE

    def on_message(self, message):
        return PopTransition([make_text_message(self.user.id, SentPictureStrings.SENT_PICTURE_MESSAGE)])
