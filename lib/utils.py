import base64
import hashlib
import hmac
import os

from google.appengine.api import users
import webapp2


def is_debug():
    return 'Development' in os.environ.get('SERVER_SOFTWARE', 'Production')


def is_admin(*args, **kwargs):
    if len(args) > 0 and isinstance(args[0], webapp2.RequestHandler):
        if args[0].request.headers.get('X-AppEngine-Cron'):
            return True
        elif args[0].request.headers.get('X-AppEngine-QueueName'):
            return True
    return users.is_current_user_admin()


def generate_signature(api_token, req_body):
    return base64.b16encode(hmac.new(str(api_token), req_body, hashlib.sha1).digest())


def messaging_url():
    return 'https://engine.apikik.com/api/v1/message'


def server_url():
    scheme = 'https' if not is_debug() else 'http'
    hostname = 'localhost:8080' if is_debug() else 'bot-dashboard.appspot.com'
    return '{}://{}'.format(scheme, hostname)


def partition(lst, size):
    """
    Partition a list into equally sized sub-lists, except the last sub-list, which may be smaller if the length
    of the input list is not evenly divisible by `size`
    :param lst: the list to partition
    :param size: the size of each sub-list
    :return: a list of sub-lists
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]
