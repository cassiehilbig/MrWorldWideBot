from google.appengine.ext import ndb

from base_model import BaseModel


class UserSessionMap(BaseModel):
    """
    Class to keep track of user session ids after the user has scanned a Kik Code, and is in the process of performing
    some kind of state-driven operation.
    """
    session_id = ndb.StringProperty(required=True, indexed=False)
    channel_token = ndb.StringProperty(required=True, indexed=False)
    last_bot_id = ndb.StringProperty(required=False, indexed=False)
    link_email = ndb.StringProperty(indexed=False)

    @property
    def id(self):
        return self.key.id()
