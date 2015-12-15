from google.appengine.ext import ndb

from test.test_base import TestBase
from model import BotUser


class TestBotUser(TestBase):
    def test_creation(self):
        self.assertEqual(BotUser().key, None)
        self.assertEqual(BotUser(id='aleem').key.id(), 'aleem')
        self.assertEqual(BotUser(id='aleem').id, 'aleem')
        self.assertEqual(BotUser(id='__aleem__').key.id(), '@__aleem__')
        self.assertEqual(BotUser(id='__aleem__').id, '__aleem__')

    def test_get_by_id(self):
        ndb.put_multi([BotUser(id='aleem'), BotUser(id='__aleem__')])
        users = [BotUser.get_by_id('aleem'), BotUser.get_by_id('__aleem__')]
        self.assertEqual([user.id for user in users], ['aleem', '__aleem__'])
        self.assertEqual([user.key.id() for user in users], ['aleem', '@__aleem__'])

    def test_states_defaults(self):
        user = BotUser()
        with self.assertRaises(AttributeError):
            id = user.id  # noqa # id never used because the `id` getter throws
        self.assertEqual(user.states, [])

        user = BotUser(id='abc', states=['a-state'])
        self.assertEqual(user.id, 'abc')
        self.assertEqual(user.states, ['a-state'])

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

    def test_generate_id(self):
        self.assertEqual(BotUser._generate_id('aleem'), 'aleem')
        self.assertEqual(BotUser._generate_id('__aleem__'), '@__aleem__')
