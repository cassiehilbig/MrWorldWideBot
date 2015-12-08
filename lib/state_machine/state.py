class State(object):
    """
    State object to be subclassed by all states in the state machine.
    """
    def __init__(self, user, *args, **kwargs):
        """
        :param user: The datastore object for the user making the request.
        """
        super(State, self).__init__(*args, **kwargs)
        self.user = user

    @staticmethod
    def type():
        """
        Type of the state. To be used for transitioning purposes.
        """
        raise NotImplementedError('State is an abstract class and should not be directly used')

    def on_message(self, message):
        """
        Handle an incoming message.
        :param message: The incoming message in json format
        :return: A Transition instance that instructs the state machine how to manipulate the user's state graph based
        on the input of the message.
        """
        raise NotImplementedError('State must return a Transition entity from its `enter` method')

    def on_resume(self):
        """
        Gives states a chance to send some contextual information back to the user when they're returning to this state
        from a stacked state that would otherwise provide the user with no useful context of the state they're being
        left in.
        :return: A Transition instance that instructs the state machine of what to do when the user falls back into this
        state from a temporary state.
        """
        return None
