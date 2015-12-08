import hashlib
from uuid import uuid4

import secrets
from config import Config
from lib import logging
from mixpanel import MixPanel


def sampling_id(username):
    return int(hashlib.sha1(username).hexdigest()[-8:], 16)


def normalized_sampling_id(username):
    # sampling ID is 4 bytes long, add 1 to the sampling ID and divide by 2^32 to normalize to the interval (0.0, 1.0]
    return (sampling_id(username) + 1) / float(2 ** 32)


def should_sample(username, sampling_rate=Config.METRICS_SAMPLING_RATE):
    normalized_id = normalized_sampling_id(username)

    # if the normalized sampling ID is less than the sampling rate, then the user is in the sample
    return normalized_id <= sampling_rate


class Metrics(object):
    def __init__(self):
        self._token = secrets.MIXPANEL_TOKEN
        self._mixpanel = MixPanel(self._token)

    #
    # Track event with parameters
    # Automatically appends current bot ID to the list of params
    #
    def track(self, event, params=None):
        if not self._token:
            logging.info('Metric ({}): {}'.format(event, params))
            return

        if params is None:
            params = {}

        params['uuid'] = str(uuid4())
        return self._mixpanel.track(event, params)

    def start_queue(self):
        self._mixpanel.start_queue()

    def stop_queue(self):
        self._mixpanel.stop_queue()
