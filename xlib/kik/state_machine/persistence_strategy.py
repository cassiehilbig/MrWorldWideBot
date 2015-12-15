class PersistenceStrategy(object):
    def get_or_create(self, entity_name):
        raise NotImplementedError

    def get_states(self, entity):
        raise NotImplementedError

    def set_states(self, entity, states):
        raise NotImplementedError

    def put(self, entity_name, entity):
        raise NotImplementedError
