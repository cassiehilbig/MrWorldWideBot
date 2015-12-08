import json
import base64

from google.appengine.api import urlfetch

from lib import logging


class MixPanel:
    MAX_BATCH_SIZE = 50

    def __init__(self, token=None):
        self._token = token
        self._is_queueing = False
        self._queue = []

    def _build_event(self, event, properties=None):
        if properties is None:
            properties
        if 'token' not in properties:
            properties['token'] = self._token
        params = {'event': event, 'properties': properties}
        return params

    def _flush_queue(self):
        queue_len = len(self._queue)

        if queue_len == 0:
            return False

        queue_boundaries = range(queue_len)[::self.MAX_BATCH_SIZE]
        subqueues = []
        for i in range(len(queue_boundaries)):
            if queue_boundaries[i] == queue_boundaries[-1]:
                subqueues.append(self._queue[queue_boundaries[i]:])
            else:
                subqueues.append(self._queue[queue_boundaries[i]:queue_boundaries[i + 1]])

        self._queue = []

        rpcs = []
        for subqueue in subqueues:
            data = "data=" + base64.b64encode(json.dumps(subqueue))
            url = 'http://api.mixpanel.com/track/?verbose=1'

            rpc = urlfetch.create_rpc()

            urlfetch.make_fetch_call(
                rpc, url, method='POST', payload=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            rpcs.append(rpc)

            logging.debug('flushed {} events from mixpanel subqueue'.format(len(subqueue)))

        return rpcs

    def start_queue(self):
        self._is_queueing = True

    def stop_queue(self):
        self._is_queueing = False
        return self._flush_queue()

    def track(self, event, properties=None):
        compiled_event = self._build_event(event, properties)
        self._queue.append(compiled_event)
        if not self._is_queueing:
            return self._flush_queue()
        return compiled_event
