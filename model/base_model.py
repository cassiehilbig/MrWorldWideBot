from datetime import datetime
from google.appengine.ext import ndb

from lib.datetime_utils import datetime_to_utc_timestamp_millis


class BaseModel(ndb.Model):
    _include = None
    _exclude = []
    _fetch_keys = True

    @classmethod
    def get_or_create(cls, id, **kwargs):
        """
        Similar to get_or_insert() but does not call put() in the case where the entity does not exist. Instead, a new,
        non-persisted entity is returned. This saves a write in cases where a property is being updated and put() is
        being called regardless of whether the entity already exists or not.
        """
        entity = cls.get_by_id(id)

        if not entity:
            entity = cls(id=id)
            entity.populate(**kwargs)

        return entity

    def to_dict(self, include=None, exclude=None, fetch_keys=None):
        """
        Converts the model into a dict
        :param exclude properties to exclude from dict; overrides all include settings
        :param include properties to include in dict; if set, properties not in include be excluded
        :param fetch_keys also fetches models from KeyProperties, and calls their to_dict() (without arguments)
        The model also has _include, _exclude, and _fetch_keys fields that act as defaults for this function.
        include will override _include, fetch_keys will override _fetch_keys, and exclude will be extended by _exclude
        """
        if include is None:
            if self._include is not None:
                include = self._include
        if exclude is None:
            exclude = []
        if fetch_keys is None:
            fetch_keys = self._fetch_keys
        exclude.extend(self._exclude)
        props = {}
        if 'id' not in exclude and (include is None or 'id' in include) and self.key:
            props['id'] = self.key.id()
        for key, prop in self._properties.iteritems():
            if key not in exclude and (include is None or key in include):
                if hasattr(self, key):
                    value = self._value_to_dict(getattr(self, key), fetch_keys)
                    props[key] = value
        return props

    def _value_to_dict(self, value, fetch_keys):
        if isinstance(value, datetime):
            return datetime_to_utc_timestamp_millis(value)
        elif isinstance(value, ndb.Key):
            if fetch_keys:
                return value.get().to_dict()
            else:
                return value.id()
        elif isinstance(value, (list, tuple)) and len(value) > 0:
            return [self._value_to_dict(val, fetch_keys) for val in value]
        return value
