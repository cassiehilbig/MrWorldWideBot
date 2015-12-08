import json
from base64 import b64encode

from google.appengine.api import urlfetch

from lib.utils import messaging_url, server_url


class SendMessagesError(Exception):
    pass


class UserInfoError(Exception):
    pass


def send_messages(messages, bot_name, bot_api_key):
    response = urlfetch.fetch(
        messaging_url(),
        method=urlfetch.POST,
        follow_redirects=False,
        payload=json.dumps({'messages': messages}),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Basic {}'.format(b64encode('{}:{}'.format(bot_name, bot_api_key)))
        }
    )
    if response.status_code != 200:
        raise SendMessagesError('Failed to send messages to engine.apikik.com. ({}) - {}'.format(
            response.status_code, json.loads(response.content)
        ))

    return json.loads(response.content)


def get_user_info(username, bot_name, bot_api_key):
    response = urlfetch.fetch(
        '{}/api/v1/user/{}'.format(server_url(), username),
        method=urlfetch.GET,
        follow_redirects=False,
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Basic {}'.format(b64encode('{}:{}'.format(bot_name, bot_api_key)))
        }
    )

    if response.status_code != 200:
        raise UserInfoError('Failed to get user info from engine.apikik.com. ({}) - {}'.format(
            response.status_code, json.loads(response.content)
        ))

    return json.loads(response.content)
