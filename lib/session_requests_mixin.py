import json

from google.appengine.api import urlfetch

from lib.bot_dashboard_request_mixin import BotDashboardRequestMixin


class SessionError(Exception):
    pass


class InvalidKikCodeError(SessionError):
    pass


class ExpiredSessionError(SessionError):
    pass


class InvalidTokenError(SessionError):
    pass


class InvalidChannelError(SessionError):
    pass


class SessionRequestsMixin(BotDashboardRequestMixin):
    def _get_user_session_from_kik_code_data(self, data, username=None):
        """
        Forwards the call on to the function that takes just the session_id
        :param data: The data that was attached to the Kik Code that was passed in.
        """
        return self._get_user_session_by_id(data['session_id'], username=username)

    def _get_user_session_by_id(self, session_id, username=None):
        """
        Ask the bot-dashboard to return a session object by passing in a Kik Code that is in the process of being used
        to establish a user's login session.
        At this point, we've already validated that the Kik Code is a dict, and it has a session_id param in it.
        :param session_id: The data that was attached to the Kik Code that was passed in.
        :raises ExpiredSessionError: If the provided session has expired
        :raises InvalidTokenError: If the provided session_id does not exist.
        :return: A session JSON object.
        """

        # Get session information from the bot-dashboard. Since we hold no truth on the state of the user in
        # bot-dashboard, this should not be cached.
        payload_json = {'session_id': session_id}
        if username:
            payload_json['username'] = username
        bot_dashboard_response = self._bot_dashboard_urlfetch(urlfetch.POST, '/session', payload_json)

        if bot_dashboard_response.status_code != 200:
            raise InvalidTokenError('No session present for login/link: {}'.format(session_id))

        return json.loads(bot_dashboard_response.content)

    def _send_session_details(self, session_id, session_data):
        """
        Sends a put request to bot-dashboard to update the current state of a particular session.
        :param session_data: The new data to write.
        :raises ExpiredSessionError: If the provided session has expired
        :raises InvalidTokenError: If the provided session_id does not exist.
        :return: None: On success, else raises.
        """
        payload_json = {'session_id': session_id, 'data': session_data}
        bot_dashboard_response = self._bot_dashboard_urlfetch(urlfetch.PUT, '/session', payload_json)

        if bot_dashboard_response.status_code == 400:
            raise ExpiredSessionError('Expired session used for update: {}'.format(payload_json))
        if bot_dashboard_response.status_code != 200:
            raise InvalidTokenError('No session present for update: {}'.format(payload_json))

        return None

    def _send_channel_data(self, channel_token, channel_data, username):
        """
        Sends a message to the bot-dashboard to be sent down an App Engine channel.
        :param channel_token: The token of the channel to send messages through.
        :param channel_data: The data that will be forwarded through the channel.
        :return: None: On success, else raises.
        """
        payload_json = {'channel_id': channel_token, 'data': channel_data, 'username': username}
        bot_dashboard_response = self._bot_dashboard_urlfetch(urlfetch.POST, '/channel', payload_json)

        if bot_dashboard_response.status_code != 200:
            raise InvalidChannelError(
                'Invalid channel data sent to bot-dashboard: {}'.format(bot_dashboard_response.content)
            )

        return None

    def _send_link_action(self, email, bot_id, username):
        payload_json = {'email': email, 'bot_id': bot_id, 'username': username}
        bot_dashboard_response = self._bot_dashboard_urlfetch(urlfetch.PUT, '/link_account', payload_json)

        if bot_dashboard_response.status_code != 200:
            raise SessionError(
                'Error occurred linking user to bot {}'.format(bot_dashboard_response.content)
            )

        return None
