from unittest import TestCase
from lib.state_machine import Transition, StackTransition, PopTransition, LambdaTransition


class TestTransition(TestCase):
    def test_transition_init(self):
        transition = Transition([], 'next-state')
        self.assertEqual(transition.messages, [])
        self.assertEqual(transition.next_state, 'next-state')

    def test_transition_init_bad_messages_type(self):
        self.assertRaises(ValueError, Transition, 'some messages', 'next-state')

    def test_stack_transition_init(self):
        transition = StackTransition([], 'next-state')
        self.assertEqual(transition.messages, [])
        self.assertEqual(transition.next_state, 'next-state')

    def test_pop_transition_init(self):
        transition = PopTransition([])
        self.assertEqual(transition.messages, [])

    def test_lambda_transition_init(self):
        transition = LambdaTransition([])
        self.assertEqual(transition.messages, [])
