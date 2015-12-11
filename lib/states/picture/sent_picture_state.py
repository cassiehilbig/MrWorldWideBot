from lib.state_machine import State, PopTransition
from lib.kik_bot import make_text_message


class SentPictureStrings(object):

    SENT_PICTURE_MESSAGE = 'Oh that\'s a cute picture!'


class SentPictureState(State):

    @staticmethod
    def type():
        return 'sent-picture'

    def on_message(self, message):
        return PopTransition([make_text_message(SentPictureStrings.SENT_PICTURE_MESSAGE, self.user.id)])