import json

from mixpanel import Mixpanel

from google.appengine.api import taskqueue
from config import Config


class EnqueuingConsumer(object):
    def send(self, endpoint, json_message):
        taskqueue.add(queue_name='mixpanel',
                      url='/tasks/mixpanel',
                      payload=json.dumps({'endpoint': endpoint, 'data': json_message}))


_mp = None


def track(id, metric, data, **kwargs):
    """
    Sends a metrics event to mixpanel

    :param id: The unique ID for this event
    :param metric: The name of the metric event
    :param data: A dictionary containing additional properties associated with this event
    :param kwargs: Additional arguments that will be passed through to Mixpanel's track function
    """
    global _mp

    if _mp is None:
        _mp = Mixpanel(Config.MIXPANEL_TOKEN, EnqueuingConsumer())

    _mp.track(id, metric, data, **kwargs)
