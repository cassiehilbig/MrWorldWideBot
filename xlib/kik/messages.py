class MessageType(object):
    LINK = 'link'
    VIDEO = 'video'
    PICTURE = 'picture'
    TEXT = 'text'
    STICKER = 'sticker'
    GROUP = 'group'
    IS_TYPING = 'is-typing'
    NATIVE_PLATFORM = 'native-platform'
    DELIVERY_RECEIPT = 'delivery-receipt'
    PUSH_RECEIPT = 'push-receipt'
    READ_RECEIPT = 'read-receipt'
    SCAN_DATA = 'scan-data'
    APP_LINK = 'app-link'
    VIRAL = 'viral'


def _make_core_message(msg_type, username, delay):
    """
    Creates the basic foundation of all message types.
    https://engine.kik.com/#/docs/messaging#common-fields
    :param msg_type: The message type of the message (https://engine.kik.com/#/docs/messaging#message-formats)
    :param username: The user that will receive the message.
    :param delay: How long to wait before delivering the message to the user.
    :return: A dictionary that can be extended with message-type specific fields.
    """
    message = {
        'type': msg_type,
        'to': username
    }

    if delay is not None:
        message['delay'] = delay

    return message


def _make_sr_message(msg_type, username, delay, suggested_responses):
    message = _make_core_message(msg_type, username, delay)
    if suggested_responses:
        message['suggestedResponses'] = suggested_responses
    return message


def make_text_message(text, username, suggested_responses=None, type_time=None, delay=None):
    """
    https://engine.kik.com/#/docs/messaging#text
    """
    message = _make_sr_message(MessageType.TEXT, username, delay, suggested_responses)
    message['body'] = text

    if type_time is not None:
        message['typeTime'] = type_time

    return message


def make_picture_message(pic_url, username, suggested_responses=None, delay=None, attribution='gallery'):
    """
    https://engine.kik.com/#/docs/messaging#picture
    """
    message = _make_sr_message(MessageType.PICTURE, username, delay, suggested_responses)
    message['picUrl'] = pic_url

    if attribution != 'gallery':
        message['attribution'] = attribution

    return message


def make_video_message(video_id, username, autoplay=False, muted=False, loop=False, suggested_responses=None,
                       delay=None, attribution='gallery'):
    """
    https://engine.kik.com/#/docs/messaging#video
    """
    message = _make_sr_message(MessageType.VIDEO, username, delay, suggested_responses)
    message.update({
        'videoId': video_id,
        'muted': muted,
        'loop': loop,
        'autoplay': autoplay
    })

    if attribution != 'gallery':
        message['attribution'] = attribution

    return message


def make_gif_message(video_id, username, suggested_responses=None, delay=None, attribution='gallery'):
    """
    :return: A video message that has been pre-formatted such that it behaves like a gif message.
    """
    return make_video_message(video_id, username, autoplay=True, muted=True, loop=True,
                              suggested_responses=suggested_responses, delay=delay, attribution=attribution)


def make_link_message(url, username, title=None, text=None, suggested_responses=None, delay=None, no_forward=None,
                      kikjs_data=None, attribution=None):
    """
    https://engine.kik.com/#/docs/messaging#link
    """
    message = _make_sr_message(MessageType.LINK, username, delay, suggested_responses)
    message.update({
        'url': url
    })

    if title is not None:
        message['title'] = title

    if text is not None:
        message['text'] = text

    if no_forward is not None:
        message['noForward'] = no_forward

    if kikjs_data is not None:
        message['kikJsData'] = kikjs_data

    if attribution is not None:
        message['attribution'] = attribution

    return message


def make_is_typing_message(is_typing, username, delay=None):
    """
    https://engine.kik.com/#/docs/messaging#is-typing
    """
    message = _make_core_message(MessageType.IS_TYPING, username, delay)
    message['isTyping'] = is_typing

    return message


def make_read_receipt_message(message_ids, username, delay=None):
    """
    https://engine.kik.com/#/docs/messaging#receipts
    """
    message = _make_core_message(MessageType.READ_RECEIPT, username, delay)
    message['messageIds'] = message_ids

    return message
