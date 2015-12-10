import json
from base64 import b64encode

from google.appengine.api import urlfetch

KIK_BOT_SERVER_FORMAT = 'https://engine.apikik.com/api/v1/{}'
KIK_BOT_MESSAGING_URL = KIK_BOT_SERVER_FORMAT.format('message')
KIK_BOT_USER_PROFILE_FORMAT = KIK_BOT_SERVER_FORMAT.format('user/{username}')
KIK_BOT_VIDEO_UPLOAD_URL = KIK_BOT_SERVER_FORMAT.format('video')

KIK_CODE_CREATION_URL = 'https://remote-scancode.kik.com/api/v1/codes'
KIK_CODE_RETRIEVAL_FORMAT = 'https://scancode.kik.com/api/v1/images/remote/{code_id}/{size}x{size}.png{color_query}'


class KikCodeColors(object):
    """
    Kik Code color mapping, taken from https://engine.kik.com/#/docs/messaging#kik-code-colors
    """
    KIK_BLUE = 0
    TURQUOISE = 1
    MINT = 2
    FOREST = 3
    KIK_GREEN = 4
    SUNSHINE = 5
    ORANGE_CREAMSICLE = 6
    BLOOD_ORANGE = 7
    CANDY_APPLE_RED = 8
    SALMON = 9
    CORAL = 10
    CRANBERRY = 11
    LAVENDER = 12
    ROYAL_PURPLE = 13
    MARINE = 14
    STEEL = 15


class KikError(Exception):
    pass


class SendMessagesError(KikError):
    pass


class UserProfileError(KikError):
    pass


class VideoUploadError(KikError):
    pass


class KikCodeGenerationError(KikError):
    pass


def send_messages(messages, bot_name, bot_api_key):
    """
    Sends messages from the bot described by the provided credentials as described in
    https://engine.kik.com/#/docs/messaging#sending-messages
    :param messages: An array of messages to be sent.
    :param bot_name: The name of the bot that is sending the messages.
    :param bot_api_key: The api key of the bot that is sending the messages.
    :return: The response from engine.apikik.com.
    :raises SendMessageError: if there is an error sending the messages.
    """
    response = urlfetch.fetch(
        KIK_BOT_MESSAGING_URL,
        method=urlfetch.POST,
        payload=json.dumps({'messages': messages}),
        headers=_generate_headers(bot_name, bot_api_key),
        deadline=60
    )
    if response.status_code != 200:
        raise SendMessagesError('Failed to send messages to engine.apikik.com. ({}) - {}'.format(
            response.status_code, response.content
        ))

    return json.loads(response.content)


def get_user_profile(username, bot_name, bot_api_key):
    """
    Lookup a user's profile from the user profile API as described in
    https://engine.kik.com/#/docs/messaging#user-profiles
    :param username: The username of the user to look up.
    :param bot_name: The username of the bot that is fetching user profile.
    :param bot_api_key: The api key of the bot that is fetching user profile.
    :return: The response from engine.apikik.com.
    :raises UserInfoError: if there is an error fetching user profile.
    """
    response = urlfetch.fetch(
        KIK_BOT_USER_PROFILE_FORMAT.format(username=username),
        method=urlfetch.GET,
        headers=_generate_headers(bot_name, bot_api_key),
        deadline=60
    )

    if response.status_code != 200:
        raise UserProfileError('Failed to get user profile from engine.apikik.com. ({}) - {}'.format(
            response.status_code, response.content
        ))

    return json.loads(response.content)


def create_video(public_video_url, bot_name, bot_api_key):
    """
    Create a video for sending in a message.
    :param public_video_url: A publicly accessible video url that will be re-hosted for public access as described in
    https://engine.kik.com/#/docs/messaging#uploading-videos
    :param bot_name: The name of the bot that is uploading the video.
    :param bot_api_key: The api key of the bot that is uploading the video.
    :return: The response from engine.apikik.com.
    :raises VideoUploadError: if there is an error uploading the video.
    """
    response = urlfetch.fetch(
        KIK_BOT_VIDEO_UPLOAD_URL,
        method=urlfetch.POST,
        payload=json.dumps({'videoUrl': public_video_url}),
        headers=_generate_headers(bot_name, bot_api_key),
        deadline=60
    )

    if response.status_code != 200:
        raise VideoUploadError('Error uploading video to engine.apikik.com. ({}) - {}'.format(
            response.status_code, response.content
        ))

    return json.loads(response.content)


def create_kik_code(bot_name, data):
    """
    Create a Kik Code as described in https://engine.kik.com/#/docs/messaging#kik-codes-api
    :param bot_name: The name of the bot whose chat should be opened when users scan the code.
    :param data: The data that will be sent to the bot when users scan the code.
    :return: The response from the remote-scancode.kik.com. Strips out the 'uri' property, and only returns 'id', as
    the `get_kik_code_url` function will allow for creating a complete url with all parameters.
    :raises KikCodeGenerationError: if there is an error creating the Kik Code.
    """
    payload = {
        'type': 'username',
        'payload': {
            'username': bot_name,
            'nonce': 0,
            'data': data if isinstance(data, basestring) else json.dumps(data)
        }
    }

    response = urlfetch.fetch(
        KIK_CODE_CREATION_URL,
        method=urlfetch.POST,
        payload=json.dumps(payload),
        headers={
            'Content-Type': 'application/json'
        },
        deadline=60
    )

    if response.status_code != 200:
        raise KikCodeGenerationError('Failed to generate the Kik Code. ({}) - {}'.format(
            response.status_code, response.content
        ))

    content = json.loads(response.content)
    del content['uri']

    return content


def get_kik_code_url(kik_code_id, size=1024, color=None):
    """
    Get the URL to a Kik Code that has already been created.
    :param kik_code_id: The ID of the Kik Code as returned in `create_kik_code`
    :param size: The width and height of the image to be returned.
    :param color: The color code of the color that will appear on screen when the user scans the Kik Code.
    :return:
    """
    if color is not None:
        return KIK_CODE_RETRIEVAL_FORMAT.format(code_id=kik_code_id, size=size, color_query='?c={}'.format(color))
    return KIK_CODE_RETRIEVAL_FORMAT.format(code_id=kik_code_id, size=size, color_query='')


def _generate_headers(bot_name, bot_api_key):
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Basic {}'.format(b64encode('{}:{}'.format(bot_name, bot_api_key)))
    }
