import json

from lib import logging
from lib.kik_bot import make_text_message
from lib.session_requests_mixin import SessionRequestsMixin, InvalidTokenError, SessionError
from lib.state_machine import State, Transition, PopTransition, LambdaTransition, ConfirmationState
from lib.states.state_types import StateTypes
from model import UserSessionMap


LINK_CODE_TYPE = 'link'


class LinkWithKikStrings(object):
    INVALID_KIK_CODE = 'I\'m sorry. This Kik Code seems to be invalid and I cannot link your Kik account to your bot'
    INVALID_TOKEN_MESSAGE = 'I\'m sorry. I won\'t be able to link yoru Kik account to your bot because that code is invalid. Please refer to the instructions on the link popup'  # noqa
    EXPIRED_TOKEN_MESSAGE = 'I\'m sorry, I won\'t be able to link your Kik account to your bot because that code has expired'  # noqa
    CONFIRMATION_MESSAGE = 'Would you like to link your Kik account to your bot?'
    SUCCESS_MESSAGE = 'Excellent. You can now access the Bot Dashboard by logging in with Kik'
    CANCELLED_MESSAGE = 'Not to worry, I\'ve cancelled linking your Kik account'
    CONFUSED_MESSAGE = 'I\'m sorry. I don\'t understand. Please say "yes" or "no"'
    CHANNEL_ERROR = 'I\'m sorry, I\'m having some trouble. Please refresh the Bot Dashboard'


class LinkWithKikChannelMessages(object):
    NO_BOTS = 'NoBots'
    EXPIRED_KEY = 'ExpiredKey'
    WAITING = 'WaitingForConfirmation'

    LINK_TERMINATED = 'LinkTerminated'
    LINK_SUCCESS = 'LinkSuccess'

    INVALID_KIK_CODE = 'InvalidKikCode'


class LinkWithKikBeginState(State, SessionRequestsMixin):
    @staticmethod
    def type():
        return StateTypes.LINK_WITH_KIK_SCAN

    def on_message(self, message):
        """
        The only message type that can enter this state is a data message with an already validated against
        isinstance(dict), and session_id in dict checks.
        """
        data = json.loads(message['data'])
        try:
            web_client_session = self._get_user_session_from_kik_code_data(data, username=self.user.id)
        except InvalidTokenError:
            return PopTransition([make_text_message(LinkWithKikStrings.INVALID_TOKEN_MESSAGE, self.user.id)])

        web_client_data = web_client_session['data']
        user_session_channel = web_client_data['code_id']

        if web_client_session['expired']:
            self._send_channel_data(user_session_channel, LinkWithKikChannelMessages.EXPIRED_KEY, message['from'])
            return PopTransition([make_text_message(LinkWithKikStrings.EXPIRED_TOKEN_MESSAGE, self.user.id)])

        if web_client_data.get('username'):
            logging.info('Consumed session used for link: {}'.format(data))
            self._send_channel_data(user_session_channel, LinkWithKikChannelMessages.EXPIRED_KEY, message['from'])
            return PopTransition([make_text_message(LinkWithKikStrings.EXPIRED_TOKEN_MESSAGE, self.user.id)])
        elif web_client_data.get('code_type') == LINK_CODE_TYPE:
            logging.debug('Linking {} to {}'.format(self.user.id, data['bot_id']))

            web_client_data['username'] = self.user.id
            self._send_session_details(web_client_session['id'], web_client_data)

            UserSessionMap(
                id=self.user.id,
                session_id=data['session_id'],
                channel_token=user_session_channel,
                last_bot_id=data['bot_id'],
                link_email=data['email']
            ).put()

            self._send_channel_data(user_session_channel, LinkWithKikChannelMessages.WAITING, message['from'])
            return Transition(
                [make_text_message(LinkWithKikStrings.CONFIRMATION_MESSAGE, self.user.id, type_time=0)],
                LinkWithKikConfirmationState.type()
            )
        else:
            return PopTransition([make_text_message(LinkWithKikStrings.INVALID_KIK_CODE, self.user.id)])

    def on_resume(self):
        return PopTransition([])


class LinkWithKikConfirmationState(ConfirmationState, SessionRequestsMixin):
    @staticmethod
    def type():
        return StateTypes.LINK_WITH_KIK_CONFIRM

    def handle_positive_response(self, message):
        user = UserSessionMap.get_by_id(message['from'])  # Has to exist if the user is in this state.

        channel_data = {
            'status': LinkWithKikChannelMessages.LINK_SUCCESS,
            'session_id': user.session_id
        }

        try:
            web_client_session = self._get_user_session_by_id(user.session_id, username=self.user.id)
        except InvalidTokenError:
            user.key.delete()
            return PopTransition([make_text_message(LinkWithKikStrings.INVALID_TOKEN_MESSAGE, self.user.id)])

        web_client_session['data']['bot'] = user.last_bot_id
        self._send_session_details(user.session_id, web_client_session['data'])

        try:
            self._send_link_action(user.link_email, user.last_bot_id, user.id)
            self._send_channel_data(user.channel_token, channel_data, message['from'])
        except SessionError as e:
            logging.error(e)
            return PopTransition([make_text_message(LinkWithKikStrings.CHANNEL_ERROR, self.user.id)])
        finally:
            user.key.delete()
        return PopTransition([make_text_message(LinkWithKikStrings.SUCCESS_MESSAGE, self.user.id)])

    def handle_negative_response(self, message):
        user = UserSessionMap.get_by_id(message['from'])  # Has to exist if the user is in this state.
        self._send_channel_data(user.channel_token, LinkWithKikChannelMessages.LINK_TERMINATED, message['from'])
        user.key.delete()
        return PopTransition([make_text_message(LinkWithKikStrings.CANCELLED_MESSAGE, self.user.id)])

    def handle_unmatched(self, message):
        return LambdaTransition([make_text_message(LinkWithKikStrings.CONFUSED_MESSAGE, self.user.id, type_time=0)])

    def on_resume(self):
        return PopTransition([])
