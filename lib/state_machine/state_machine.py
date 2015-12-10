import sys

from transition import Transition, PopTransition, StackTransition, LambdaTransition
from keyword_state import KeywordState


class StateMachine(object):
    """
    The StateMachine class handles sending messages into the states defined by client logic.
    """
    def __init__(self, default_state):
        super(StateMachine, self).__init__()
        self._states = {}
        self._global_interceptors = []
        self._default_state = default_state
        self.register_state(self._default_state)

    def register_state(self, state):
        self._states[state.type()] = state

    def get_state(self, state_name):
        try:
            return self._states[state_name]
        except KeyError:
            raise KeyError('Attempted to load non-existent state, {}'.format(state_name)), None, sys.exc_info()[2]

    def register_global_interceptor(self, fn):
        """
        Global interceptors are run before any state logic is executed, and are allowed to update the user's state stack
        in order to force the user into a different state based on their input.
        :param fn: A fn(user, messages): that tests for certain conditions on the user object or message object. These
        functions should return True if they with to stop additional global interceptors from being executed.
        """
        self._global_interceptors.append(fn)

    def handle_message(self, user, message):
        """
        Get a message from the chat engine, process it, and return the results.
        :param message: The incoming message in json format
        :return: A list of valid Chat Engine messages that can be sent to the user via the Chat Engine API.
        """
        for fn in self._global_interceptors:
            if fn(user, message):
                break

        state = self._get_user_current_state(user)

        transition = state.on_message(message)
        if not isinstance(transition, Transition):
            raise ValueError('State.enter() must return a Transition object.')

        messages = self.handle_transition(user, transition)
        user_next_state = self._get_user_current_state(user)
        if isinstance(user_next_state, KeywordState) and user_next_state.suggested_responses:
            messages[-1]['suggestedResponses'] = user_next_state.suggested_responses

        return messages

    def handle_transition(self, user, transition):
        """
        Handle a transition that was returned by a state. May need to recurse through itself in the event that a state's
        fallback requests that it transitions to a different state from the fallback.
        """
        if isinstance(transition, PopTransition):
            user.states.pop()
            entering_state = self._get_user_current_state(user)
            fallback = entering_state.on_resume()
            if fallback:
                fallback.messages = transition.messages + fallback.messages
                return self.handle_transition(user, fallback)
        elif isinstance(transition, StackTransition):
            user.states.append(transition.next_state)
        elif isinstance(transition, LambdaTransition):
            pass
        elif isinstance(transition, Transition):
            user.states[-1] = transition.next_state
        else:
            raise ValueError('StateMachine.handle_transition called with non Transition entity.')

        return transition.messages

    def _get_user_current_state(self, user):
        if not user.states:
            user.states = [self._default_state.type()]
        state_name = user.states[-1]
        state = self.get_state(state_name)

        return state(user)