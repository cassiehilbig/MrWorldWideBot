from google.appengine.ext import ndb

from base_model import BaseModel
from lib.admin_requests_mixin import AdminRequestsMixin


class BotUser(BaseModel, AdminRequestsMixin):
    states = ndb.StringProperty(indexed=False, repeated=True)
    state_data = ndb.JsonProperty(indexed=False)

    def __init__(self, *args, **kwargs):
        super(BotUser, self).__init__(*args, **kwargs)
        self._admin_cache = None
        self.state_data = self.state_data or {}

    @property
    def id(self):
        return self.key.id()

    def bots(self):
        return [admin_bot['id'] for admin_bot in self.get_admin()['bots']]

    def get_admin(self):
        if self._admin_cache is None:
            self._admin_cache = self._get_admin(self.id)
        return self._admin_cache

    def get_state_data(self, state):
        if self.state_data.get(state) is None:
            self.state_data[state] = {}
        return self.state_data[state]

    def current_state_data(self):
        if len(self.states) == 0:
            raise Exception('User has no state yet')
        return self.get_state_data(self.states[-1])

    def clear_current_state_data(self):
        if len(self.states) == 0:
            raise Exception('User has no state yet')
        state_name = self.states[-1]
        if state_name in self.state_data:
            del self.state_data[state_name]
