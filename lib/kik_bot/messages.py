from const import MessageType


def make_text_message(text, username, suggested_responses=None, type_time=None):
    message = {
        'type': MessageType.TEXT,
        'body': text,
        'to': username
    }

    if suggested_responses:
        message['suggestedResponses'] = suggested_responses

    if type_time is not None:
        message['typeTime'] = type_time

    return message


def make_video_message(video_id, username, gif=False, suggested_responses=None):
    message = {
        'type': MessageType.VIDEO,
        'to': username,
        'videoId': video_id,
        'muted': gif,
        'loop': gif,
        'autoplay': gif
    }

    if suggested_responses:
        message['suggestedResponses'] = suggested_responses

    return message


def make_link_message(url, title, text, username, suggested_responses=None):
    message = {
        'type': MessageType.LINK,
        'to': username,
        'url': url,
        'title': title,
        'text': text
    }

    if suggested_responses:
        message['suggestedResponses'] = suggested_responses

    return message
