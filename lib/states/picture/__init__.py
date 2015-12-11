from kik import MessageType
from sent_picture_state import SentPictureState


def picture_interceptor(user, message):
    if message['type'] == MessageType.PICTURE:
        user.states.append('sent-picture')
        return True
    return False

__all__ = ['picture_interceptor', 'SentPictureState']
