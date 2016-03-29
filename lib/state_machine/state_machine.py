import sys

from transition import Transition, PopTransition, StackTransition, LambdaTransition, JumpTransition
from keyword_state import KeywordState
from lib.message_types import MessageType
from kik.messages.keyboards import SuggestedResponseKeyboard


class StateMachine(object):
    """
    The StateMachine class handles sending messages into the states defined by client logic.
    """
    def __init__(self, default_state, persistence_strategy=None):
        super(StateMachine, self).__init__()
        self._states = {}
        self._global_interceptors = []
        self._default_state = default_state
        self.register_state(self._default_state)
        self.persistence_strategy = persistence_strategy

    def register_state(self, state):
        if state.type() in self._states and state != self._states[state.type()]:
            raise ValueError('Attempted to register two different states with the same ID ({})'.format(state.type()))
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

    def handle_message(self, username, message):
        """
        Get a message from the chat engine, process it, and return the results.
        :param message: The incoming message in json format
        :return: A list of valid Chat Engine messages that can be sent to the user via the Chat Engine API.
        """
        if self.persistence_strategy is None:
            raise AssertionError('persistence_strategy must be set for state_machine')

        user = self.persistence_strategy.get_or_create(username)
        if user is None:
            raise AssertionError('A user must be returned by the persistence_strategy')

        self.repair_user_state_inconsistency(user)

        for fn in self._global_interceptors:
            if fn(user, message):
                break

        state = self._get_user_current_state(user)

        transition = state.on_message(message)
        if not isinstance(transition, Transition):
            raise ValueError('State.on_message() must return a Transition object.')

        messages = self.handle_transition(user, transition)
        user_next_state = self._get_user_current_state(user)
        if isinstance(user_next_state, KeywordState) and user_next_state.suggested_responses and messages:
            if not getattr(messages[-1], 'keyboards') and messages[-1].type not in MessageType.TRANSIENT:
                messages[-1].keyboards = [SuggestedResponseKeyboard(responses=user_next_state.suggested_responses)]

        self.persistence_strategy.put(username, user)

        return messages

    def handle_transition(self, user, transition):
        """
        Handle a transition that was returned by a state. May need to recurse through itself in the event that a state's
        fallback requests that it transitions to a different state from the fallback.
        """
        states = self.persistence_strategy.get_states(user)
        if isinstance(transition, PopTransition):
            print "ihfisherfihersfhuiersfhiesuhrfhsuefuihfiruhef"
            states.pop()

            # We just made the user go to a state he used to be in. This state might need to be repaired
            self.repair_user_state_inconsistency(user)

            self.persistence_strategy.set_states(user, states)
            entering_state = self._get_user_current_state(user)
            fallback = entering_state.on_resume()
            if fallback:
                fallback.messages = transition.messages + fallback.messages
                return self.handle_transition(user, fallback)
        elif isinstance(transition, StackTransition):
            states = self.persistence_strategy.get_states(user)
            states.append(transition.next_state)
            self.persistence_strategy.set_states(user, states)
        elif isinstance(transition, LambdaTransition):
            pass
        elif isinstance(transition, JumpTransition):
            states = transition.new_states
            self.persistence_strategy.set_states(user, states)
        elif isinstance(transition, Transition):
            states = self.persistence_strategy.get_states(user)
            states[-1] = transition.next_state
            self.persistence_strategy.set_states(user, states)
        else:
            raise ValueError('StateMachine.handle_transition called with non Transition entity.')

        return transition.messages

    def repair_user_state_inconsistency(self, user):
        """
        Repairs a user's state stack. Sometimes after a code change a user can end up in a state that does not exist.
        :param user: The user object to fix
        """

        states = self.persistence_strategy.get_states(user)

        while len(states) > 0 and states[-1] not in self._states:
            states.pop()

        self.persistence_strategy.set_states(user, states)

    def _get_user_current_state(self, user):
        states = self.persistence_strategy.get_states(user)
        if not states:
            states = [self._default_state.type()]
            self.persistence_strategy.set_states(user, states)
        state_name = states[-1]
        state = self.get_state(state_name)

        return state(user)
