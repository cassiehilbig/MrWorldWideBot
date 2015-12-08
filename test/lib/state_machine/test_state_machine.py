from unittest import TestCase
from lib.state_machine import State, StateMachine, Transition, LambdaTransition, PopTransition, StackTransition


# Define a bunch of test states that transition in different ways so that we can test all different state machine
# interactions.
class DefaultState(State):
    @staticmethod
    def type():
        return 'default'

    def on_message(self, message):
        return LambdaTransition(['a default message'])


class AlwaysTransitionsState(State):
    @staticmethod
    def type():
        return 'state'

    def on_message(self, message):
        return Transition(['a transition message'], 'next-state')


class AlwaysLambdaTransitionState(State):
    @staticmethod
    def type():
        return 'lambda-state'

    def on_message(self, message):
        return LambdaTransition(['a lambda message'])


class AlwaysPopTransitionState(State):
    @staticmethod
    def type():
        return 'pop-state'

    def on_message(self, message):
        return PopTransition(['a pop message'])


class AlwaysStackTransitionState(State):
    @staticmethod
    def type():
        return 'stack-state'

    def on_message(self, message):
        return StackTransition(['a stack message'], 'next-state')


class PreviousState(State):
    @staticmethod
    def type():
        return 'previous-state'

    def on_message(self, message):
        return LambdaTransition([])


class NextState(State):
    @staticmethod
    def type():
        return 'next-state'

    def on_message(self, message):
        return LambdaTransition([])

    def on_resume(self):
        return LambdaTransition(['a fallback message'])


class TotallyBrokenState(State):
    @staticmethod
    def type():
        return 'broken-state'

    def on_message(self, message):
        return 'a message'

    def on_resume(self):
        return 'another message'


def interceptor(user, message):
    if message == 'intercept me':
        user.states.append('lambda-state')
        return True


testing_state_machine = StateMachine(DefaultState)


testing_state_machine.register_state(AlwaysTransitionsState)
testing_state_machine.register_state(AlwaysStackTransitionState)
testing_state_machine.register_state(AlwaysPopTransitionState)
testing_state_machine.register_state(AlwaysLambdaTransitionState)
testing_state_machine.register_state(PreviousState)
testing_state_machine.register_state(NextState)
testing_state_machine.register_state(TotallyBrokenState)

testing_state_machine.register_global_interceptor(interceptor)


class StateMachineTestUser(object):
    def __init__(self, states):
        self.states = states


class TestStateMachine(TestCase):
    def test_get_state(self):
        self.assertEqual(testing_state_machine.get_state('next-state'), NextState)

    def test_get_non_existent_state(self):
        self.assertRaises(KeyError, testing_state_machine.get_state, 'not a state')

    def test_uses_default_state(self):
        user = StateMachineTestUser([])
        messages = testing_state_machine.handle_message(user, 'yo')
        self.assertEqual(messages, ['a default message'])

    def test_handle_message_to_state_that_transitions(self):
        user = StateMachineTestUser(['previous-state', 'state'])
        messages = testing_state_machine.handle_message(user, 'hello')
        self.assertEqual(user.states, ['previous-state', 'next-state'])
        self.assertEqual(messages, ['a transition message'])

    def test_handle_message_to_state_that_lambda_transitions(self):
        user = StateMachineTestUser(['previous-state', 'lambda-state'])
        messages = testing_state_machine.handle_message(user, 'hello')
        self.assertEqual(user.states, ['previous-state', 'lambda-state'])
        self.assertEqual(messages, ['a lambda message'])

    def test_handle_message_to_state_that_pop_transitions(self):
        user = StateMachineTestUser(['previous-state', 'pop-state'])
        messages = testing_state_machine.handle_message(user, 'hello')
        self.assertEqual(user.states, ['previous-state'])
        self.assertEqual(messages, ['a pop message'])

    def test_handle_message_to_state_that_stack_transitions(self):
        user = StateMachineTestUser(['previous-state', 'stack-state'])
        messages = testing_state_machine.handle_message(user, 'hello')
        self.assertEqual(user.states, ['previous-state', 'stack-state', 'next-state'])
        self.assertEqual(messages, ['a stack message'])

    def test_handle_message_causes_fallback(self):
        user = StateMachineTestUser(['previous-state', 'next-state', 'pop-state'])
        messages = testing_state_machine.handle_message(user, 'hello')
        self.assertEqual(messages, ['a pop message', 'a fallback message'])

    def test_handle_message_transition_sends_no_messages(self):
        user = StateMachineTestUser(['previous-state', 'next-state'])
        messages = testing_state_machine.handle_message(user, 'hello')
        self.assertEqual(messages, [])

    def test_malformed_state(self):
        user = StateMachineTestUser(['broken-state'])
        self.assertRaises(ValueError, testing_state_machine.handle_message, user, 'hello')

    def test_handle_transition_not_a_transition(self):
        user = StateMachineTestUser(['previous-state'])
        self.assertRaises(ValueError, testing_state_machine.handle_transition, user, 'I\'m a transition. Promise')

    def test_global_interceptor(self):
        user = StateMachineTestUser(['next-state'])

        testing_state_machine.handle_message(user, 'intercept me')
        self.assertEqual(user.states, ['next-state', 'lambda-state'])
