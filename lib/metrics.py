import json

from mixpanel import Mixpanel

from google.appengine.api import taskqueue
from config import Config


class EnqueuingConsumer(object):
    def send(self, endpoint, json_message):
        taskqueue.add(queue_name='mixpanel',
                      url='/tasks/mixpanel',
                      payload=json.dumps({'endpoint': endpoint, 'data': json_message}))


_mp = Mixpanel(Config.MIXPANEL_TOKEN, EnqueuingConsumer())


def track(user, type, data, **kwargs):
    if len(user.states) > 0:
        data['state'] = user.states[-1]

    _mp.track(user.id, type, data, **kwargs)
