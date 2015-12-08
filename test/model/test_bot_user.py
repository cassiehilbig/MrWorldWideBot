import mock

from test.test_base import TestBase
from model import BotUser


class TestBotUser(TestBase):
    def test_states_defaults(self):
        user = BotUser()
        with self.assertRaises(AttributeError):
            id = user.id  # noqa # id never used because the `id` getter throws
        self.assertEqual(user.states, [])

        user = BotUser(id='abc', states=['a-state'])
        self.assertEqual(user.id, 'abc')
        self.assertEqual(user.states, ['a-state'])

    @mock.patch(
        'lib.admin_requests_mixin.AdminRequestsMixin._get_admin',
        return_value={'bots': [{'id': 'a'}, {'id': 'b'}]}
    )
    def test_get_admin(self, get_admin):
        user = BotUser(id='abc')
        self.assertEqual(user.get_admin(), {'bots': [{'id': 'a'}, {'id': 'b'}]})
        self.assertEqual(get_admin.call_count, 1)
        self.assertEqual(user.get_admin(), {'bots': [{'id': 'a'}, {'id': 'b'}]})
        self.assertEqual(get_admin.call_count, 1)

    @mock.patch(
        'lib.admin_requests_mixin.AdminRequestsMixin._get_admin',
        return_value={'bots': [{'id': 'a'}, {'id': 'b'}]}
    )
    def test_get_bots(self, get_admin):
        user = BotUser(id='abc')
        self.assertEqual(user.bots(), ['a', 'b'])
        self.assertEqual(get_admin.call_count, 1)
        self.assertEqual(user.bots(), ['a', 'b'])
        self.assertEqual(get_admin.call_count, 1)

    def test_get_state_data_default(self):
        user = BotUser()

        self.assertEqual(user.get_state_data('foo'), {})
        self.assertEqual(user.get_state_data('bar'), {})

    def test_get_state_data_initialized(self):
        user = BotUser(state_data={'foo': {'bar': 'baz'}})

        self.assertEqual(user.get_state_data('foo'), {'bar': 'baz'})

    def test_current_state_data_no_state(self):
        user = BotUser()
        self.assertRaises(Exception, user.current_state_data)

    def test_current_state_data_initialized(self):
        user = BotUser(states=['yolo', 'foo'], state_data={'foo': {'bar': 'baz'}})

        self.assertEqual(user.current_state_data(), {'bar': 'baz'})

    def test_current_state_data_not_initialized(self):
        user = BotUser(states=['yolo', 'foo'])

        self.assertEqual(user.current_state_data(), {})

    def test_clear_current_state_data(self):
        user = BotUser(states=['some_state'])
        state_data = user.current_state_data()
        state_data['a'] = 'b'
        state_data['key'] = 'value'
        self.assertEqual(user.current_state_data(), {'a': 'b', 'key': 'value'})
        user.clear_current_state_data()
        self.assertEqual(user.current_state_data(), {})

    def test_clear_current_state_data_no_states(self):
        user = BotUser()
        self.assertRaises(user.clear_current_state_data)
