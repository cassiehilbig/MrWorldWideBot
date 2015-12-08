from model import BotUser
from test.test_base import TestBase
from const import MessageType
from lib.state_machine import PopTransition, LambdaTransition
from lib.states.select_bot_name_state import SelectBotNameState, SelectBotNameStateStrings


class SelectBotNameStateTest(TestBase):
    def test_is_abstract(self):
        user = BotUser(id='aleem')
        inst = SelectBotNameState(user)
        self.assertRaises(NotImplementedError, inst.type)
        self.assertRaises(NotImplementedError, inst.on_bot_name_message, 'who cares it\'s not implemented anyways')

    def test_suggested_responses(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': name} for name in ['0', '1', '2', '3', '4', '5']]}

        inst = SelectBotNameState(user)

        self.assertEqual(inst.get_suggested_responses(), ['0', '1', '2', '3', '4', '5', 'Cancel'])

    def test_suggested_responses_rolls_over(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': name} for name in ['0', '1', '2', '3', '4', '5', '6']]}

        inst = SelectBotNameState(user)

        self.assertEqual(inst.get_suggested_responses(), ['0', '1', '2', '3', '4', 'More', 'Cancel'])

    def test_suggested_responses_rolled_over(self):
        user = BotUser(id='aleem')
        user._admin_cache = {'bots': [{'id': name} for name in ['0', '1', '2', '3', '4', '5', '6']]}
        user.states = ['some-state-that-implements-select-bot-name']
        user.state_data['some-state-that-implements-select-bot-name'] = {
            'offset': 5
        }

        inst = SelectBotNameState(user)

        self.assertEqual(inst.get_suggested_responses(), ['5', '6', 'More', 'Cancel'])

    def test_suggested_responses_even_more_bots(self):
        user = BotUser(id='aleem')
        user._admin_cache = {
            'bots': [{'id': name} for name in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']]
        }
        user.states = ['some-state-that-implements-select-bot-name']
        user.state_data['some-state-that-implements-select-bot-name'] = {
            'offset': 5
        }

        inst = SelectBotNameState(user)

        self.assertEqual(inst.get_suggested_responses(), ['05', '06', '07', '08', '09', 'More', 'Cancel'])

    def test_suggested_responses_sorted(self):
        user = BotUser(id='aleem')
        user._admin_cache = {
            'bots': [{'id': name} for name in ['c', 'd', 'a', 'b', 'e']]
        }
        user.states = ['some-state-that-implements-select-bot-name']

        inst = SelectBotNameState(user)

        self.assertEqual(inst.get_suggested_responses(), ['a', 'b', 'c', 'd', 'e', 'Cancel'])

    def test_on_message_is_a_bot(self):
        user = BotUser(id='aleem')
        user._admin_cache = {'bots': [{'id': 'a'}]}
        user.states = ['some-state-that-implements-select-bot-name']

        inst = SelectBotNameState(user)
        self.assertRaises(NotImplementedError, inst.on_message, {'type': MessageType.TEXT, 'body': 'a'})

    def test_on_message_is_cancel(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': {'id': name} for name in ['a', 'b', 'c', 'd', 'e', 'f']}
        user.current_state_data()['offset'] = 5

        inst = SelectBotNameState(user)
        transition = inst.on_message({'type': MessageType.TEXT, 'body': 'cancel'})
        self.assertIsInstance(transition, PopTransition)
        self.assertEqual(transition.messages, [])
        self.assertNotIn('offset', user.current_state_data())

    def test_on_message_more_are_no_more(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': 'a'}]}

        inst = SelectBotNameState(user)
        transition = inst.on_message({'type': MessageType.TEXT, 'body': 'more'})
        self.assertIsInstance(transition, LambdaTransition)
        self.assertEqual(transition.messages, [{
            'type': MessageType.TEXT,
            'body': SelectBotNameStateStrings.MORE_RESPONSE_TEXT,
            'to': 'aleem',
            'suggestedResponses': ['a', 'Cancel']
        }])

        self.assertEqual(user.current_state_data()['offset'], 0)

    def test_on_message_more_gives_more_results(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': name} for name in ['a', 'b', 'd', 'e', 'f', 'g', 'h']]}

        inst = SelectBotNameState(user)
        transition = inst.on_message({'type': MessageType.TEXT, 'body': 'more'})
        self.assertIsInstance(transition, LambdaTransition)
        self.assertEqual(transition.messages, [{
            'type': MessageType.TEXT,
            'body': SelectBotNameStateStrings.MORE_RESPONSE_TEXT,
            'to': 'aleem',
            'suggestedResponses': ['g', 'h', 'More', 'Cancel']
        }])

    def test_on_message_more_gives_original_results_when_rolls_over(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': name} for name in 'a', 'b', 'd', 'e', 'f', 'g', 'h']}
        user.current_state_data()['offset'] = 5

        inst = SelectBotNameState(user)
        transition = inst.on_message({'type': MessageType.TEXT, 'body': 'more'})
        self.assertIsInstance(transition, LambdaTransition)
        self.assertEqual(transition.messages, [{
            'type': MessageType.TEXT,
            'body': SelectBotNameStateStrings.MORE_RESPONSE_TEXT,
            'to': 'aleem',
            'suggestedResponses': ['a', 'b', 'd', 'e', 'f', 'More', 'Cancel']
        }])
        self.assertEqual(user.current_state_data()['offset'], 0)

    def test_on_bot_name_message_offset_reset(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': name} for name in ['a', 'b', 'd', 'e', 'f', 'g', 'h']]}
        user.current_state_data()['offset'] = 5

        inst = SelectBotNameState(user)
        with self.assertRaises(NotImplementedError):
            inst.on_message({'type': MessageType.TEXT, 'body': 'a'})

        self.assertNotIn('offset', user.current_state_data())

    def test_on_message_gibberish_not_a_bot_name(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': 'a'}]}

        inst = SelectBotNameState(user)
        transition = inst.on_message({'type': MessageType.TEXT, 'body': 'I like turtles'})
        self.assertIsInstance(transition, LambdaTransition)
        self.assertEqual(transition.messages, [{
            'type': MessageType.TEXT,
            'body': SelectBotNameStateStrings.NO_BOT_FOUND_TEXT,
            'to': 'aleem',
            'suggestedResponses': ['a', 'Cancel']
        }])

    def test_on_message_gibberish_not_a_text_message(self):
        user = BotUser(id='aleem')
        user.states = ['some-state-that-implements-select-bot-name']
        user._admin_cache = {'bots': [{'id': 'a'}]}

        inst = SelectBotNameState(user)
        transition = inst.on_message({'type': MessageType.PICTURE, 'picUrl': 'http://www.example.com/test.png'})
        self.assertIsInstance(transition, LambdaTransition)
        self.assertEqual(transition.messages, [{
            'type': MessageType.TEXT,
            'body': SelectBotNameStateStrings.UNKNOWN_MESSAGE_TYPE_TEXT,
            'to': 'aleem',
            'suggestedResponses': ['a', 'Cancel']
        }])
