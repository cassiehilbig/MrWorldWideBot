import json

from const import MessageType
from lib import logging
from link_with_kik_flow import LinkWithKikBeginState, LinkWithKikConfirmationState
from lib.states.state_types import StateTypes


def link_state_interceptor(user, message):
    if message['type'] == MessageType.SCAN_DATA:
        try:
            """
            If json.loads fails, just fall through to whatever state the user is currently in. Let it handle the
            incoming message normally.
            """
            message_data = json.loads(message['data'])
        except ValueError as e:
            logging.info(e.message)
            return False

        if isinstance(message_data, dict) \
                and 'session_id' in message_data and 'email' in message_data and 'bot_id' in message_data:
            user.states.append(StateTypes.LINK_WITH_KIK_SCAN)
            return True
    return False

__all__ = ['LinkWithKikBeginState', 'LinkWithKikConfirmationState', 'link_state_interceptor']
