from unittest import TestCase
from lib.state_machine import State


class TestState(TestCase):
    def test_state_init(self):
        state = State('a_user!')
        self.assertEqual(state.user, 'a_user!')

    def test_state_type_error(self):
        self.assertRaises(NotImplementedError, State.type)

    def test_state_enter(self):
        self.assertRaises(NotImplementedError, State('user').on_message, 'msg')

    def test_state_fallback(self):
        self.assertEqual(State('user').on_resume(), None)
