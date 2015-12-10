class Transition(object):
    """
    Encapsulates an edge of the state machine. Contains a list of messages that give the user information about their
    current state and the actions that they can take from their current situation.
    """
    def __init__(self, messages, next_state):
        super(Transition, self).__init__()
        if type(messages) not in (list, tuple):
            raise ValueError('Transition messages must be a list or tuple.')

        self.messages = messages
        self.next_state = next_state


class StackTransition(Transition):
    """
    Transition subclass that adds an element to the user's state list without interfering with the user's current state
    list.
    """
    pass


class PopTransition(Transition):
    """
    Transition subclass that should only remove the current state from the user's state graph, and lead the user into
    the fallback message of the previous state that they were in.
    """
    def __init__(self, messages):
        super(PopTransition, self).__init__(messages, None)


class LambdaTransition(Transition):
    """
    Transition subclass that does not change the user's state list in any way. Just sends mesages.
    """
    def __init__(self, messages):
        super(LambdaTransition, self).__init__(messages, None)
