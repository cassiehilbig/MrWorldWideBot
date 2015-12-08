import json

from google.appengine.api import urlfetch

from lib.bot_dashboard_request_mixin import BotDashboardRequestMixin
from lib import logging


class AdminFetchError(Exception):
    pass


class CreateBotError(Exception):
    pass


class UsernameAvailableCheckError(Exception):
    pass


class UpdateDisplayNameError(Exception):
    pass


class UpdateProfilePictureError(Exception):
    pass


class AdminRequestsMixin(BotDashboardRequestMixin):
    def _get_admin(self, username):
        """
        Gets an admin model from the bot dashboard.
        :param username: The username of the admin to fetch.
        """
        resource = '/admin?username={}'.format(username)
        response = self._bot_dashboard_urlfetch(urlfetch.GET, resource)

        if response.status_code != 200:
            raise AdminFetchError('Failed to fetch admin information ({}) - {}'.format(
                response.status_code, response.content
            ))

        return json.loads(response.content)

    def _check_username_available(self, username):
        resource = '/username_available?username={}'.format(username)
        response = self._bot_dashboard_urlfetch(urlfetch.GET, resource)

        if response.status_code != 200:
            raise UsernameAvailableCheckError('Failed to fetch admin information ({}) - {}'.format(
                                              response.status_code,
                                              response.content))

        return json.loads(response.content)

    def _create_bot(self, username, bot_id, display_name):
        """
        Creates a bot on the bot dashboard and the Kik servers.
        :param username: The admin username
        :param bot_id: The bot ID to be used
        :param display_name: The bot's display name
        """
        payload = {
            'username': username,
            'bot_id': bot_id,
            'display_name': display_name
        }
        response = self._bot_dashboard_urlfetch(urlfetch.POST, '/bot/create', payload_json=payload)

        if response.status_code != 200:
            raise CreateBotError('Failed to create bot ({}) - {}'.format(response.status_code, response.content))

        return json.loads(response.content)

    def _update_bot_display_name(self, username, bot_id, new_display_name):
        """
        Send a request off to the bot-dashboad to update a bot's display name
        :param username: The name of the user making the request.
        :param bot_id: The bot_id of the bot that will be affected..
        :param new_display_name: The new display name to be set on the bot.
        """
        resource = '/bot/{}/display_name'.format(bot_id)
        payload = {
            'username': username,
            'display_name': new_display_name
        }
        response = self._bot_dashboard_urlfetch(urlfetch.PUT, resource, payload)

        if response.status_code != 200:
            logging.info(payload)
            raise UpdateDisplayNameError('Failed to update bot display name ({}) - {}'.format(
                response.status_code, response.content
            ))

        return json.loads(response.content)

    def _update_bot_profile_picture(self, username, bot_id, profile_picture_url):
        """
        Send a request off to the bot-dashboad to update a bot's profile picture
        :param username: The name of the user making the request.
        :param bot_id: The bot_id of the bot that will be affected..
        :param profile_picture_url: A url to the new profile picture for the bot.
        """
        resource = '/bot/{}/profile_picture'.format(bot_id)
        payload = {
            'username': username,
            'profile_picture': profile_picture_url
        }
        response = self._bot_dashboard_urlfetch(urlfetch.PUT, resource, payload)

        if response.status_code != 200:
            logging.info(payload)
            raise UpdateProfilePictureError('Failed to update bot profile picture ({}) - {}'.format(
                response.status_code, response.content
            ))

        return json.loads(response.content)
