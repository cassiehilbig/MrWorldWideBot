import base64
import hashlib
import hmac
import os
import json


def is_debug():
    return 'Development' in os.environ.get('SERVER_SOFTWARE', 'Production')


def generate_signature(api_token, req_body):
    return base64.b16encode(hmac.new(str(api_token), req_body, hashlib.sha1).digest())


def partition(lst, size):
    """
    Partition a list into equally sized sub-lists, except the last sub-list, which may be smaller if the length
    of the input list is not evenly divisible by `size`
    :param lst: the list to partition
    :param size: the size of each sub-list
    :return: a list of sub-lists
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def error_response(status_code, message=None):
    return json.dumps({
        'message': message
    }), status_code
