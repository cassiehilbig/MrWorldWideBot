from google.appengine.ext import ndb

from base_model import BaseModel


class BotUser(BaseModel):
    states = ndb.StringProperty(indexed=False, repeated=True)
    state_data = ndb.JsonProperty(indexed=False)

    def __init__(self, *args, **kwargs):
        super(BotUser, self).__init__(*args, **kwargs)
        self._admin_cache = None
        self.state_data = self.state_data or {}

    @property
    def id(self):
        return self.key.id()

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
