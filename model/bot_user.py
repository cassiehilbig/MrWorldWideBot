from google.appengine.ext import ndb

from base_model import BaseModel


class BotUser(BaseModel):
    states = ndb.StringProperty(indexed=False, repeated=True)
    state_data = ndb.JsonProperty(indexed=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            kwargs['id'] = self._generate_id(kwargs['id'])
        super(BotUser, self).__init__(*args, **kwargs)
        self.state_data = self.state_data or {}

    @classmethod
    def get_by_id(cls, id, *args, **kwargs):
        return super(BotUser, cls).get_by_id(cls._generate_id(id), *args, **kwargs)

    @property
    def id(self):
        username = self.key.id()
        if username.startswith('@__') and username.endswith('__'):
            return username[1:]
        return username

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

    @classmethod
    def _generate_id(cls, id):
        if id.startswith('__') and id.endswith('__'):
            id = '@' + id
        return id.lower()
