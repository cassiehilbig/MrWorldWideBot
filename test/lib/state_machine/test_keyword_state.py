from unittest import TestCase
from lib.state_machine import State, KeywordState, LambdaTransition, keyword_response, StateMachine

"""
Order is a super hacky way of keeping track of the order of suggested response and keyword ordering. Because of its
scope, it affects other state machines that exist in memory, so other state machines affect the global value.
We have to use it to dictate ordering.
"""
from lib.state_machine.keyword_state import order


class DefaultState(State):

    @staticmethod
    def type():
        return 'foo'


class BasicKeywordState(KeywordState):
    @staticmethod
    def type():
        return 'keyword-state'

    @keyword_response('#1')
    def keyword_1(self, message):
        return LambdaTransition([{'body': 'You sent #1!'}])

    @keyword_response('#2', 'two')
    def keyword_2(self, message):
        return LambdaTransition([{'body': 'You sent #2!'}])

    def handle_unmatched(self, message):
        return LambdaTransition([{'body': 'I can\'t handle that message.'}])


class AdditionalKeywordState(KeywordState):
    @staticmethod
    def type():
        return 'another-keyword-state'

    @keyword_response('#2', '2', 'second')
    def keyword_2(self, message):
        return LambdaTransition([{'body': 'You sent #2!'}])

    def handle_unmatched(self, message):
        return LambdaTransition([{'body': 'Can you try that again for me?'}])


class NoKeywordsState(KeywordState):
    @staticmethod
    def type():
        return 'keywordless-state'

    def handle_unmatched(self, message):
        return LambdaTransition([{'body': 'Lol, didn\'t read.'}])


class CapitalizedKeywordState(KeywordState):
    @staticmethod
    def type():
        return 'capitals-state'

    @keyword_response('Yes', 'yes')
    def handle_word1(self, message):
        return LambdaTransition([])

    @keyword_response('No', 'no')
    def handle_word2(self, message):
        return LambdaTransition([])

    def handle_unmatched(self, message):
        raise NotImplementedError()


class RegExpyKeywordState(KeywordState):
    @staticmethod
    def type():
        return 'regex-state'

    @keyword_response('\\byolo\\b')
    def handle_word1(self, message):
        return LambdaTransition([{'body': 'yolo'}])

    def handle_unmatched(self, message):
        return LambdaTransition([{'body': 'nope'}])


testing_state_machine = StateMachine(DefaultState)

testing_state_machine.register_state(BasicKeywordState)
testing_state_machine.register_state(AdditionalKeywordState)
testing_state_machine.register_state(NoKeywordsState)
testing_state_machine.register_state(CapitalizedKeywordState)
testing_state_machine.register_state(RegExpyKeywordState)


class StateMachineTestUser(object):
    def __init__(self, states):
        self.states = states


class TestKeywordState(TestCase):
    def test_creation(self):
        user = StateMachineTestUser([])

        inst = BasicKeywordState(user)
        self.assertEqual(len(inst.keyword_responses), 2)
        self.assertEqual(inst.keyword_responses[0].order, order)
        self.assertEqual(inst.keyword_responses[0].regexp.pattern, r'(^|\s|\b)(\#1)($|\s|\b)')
        self.assertEqual(inst.keyword_responses[1].order, order + 1)
        self.assertEqual(inst.keyword_responses[1].regexp.pattern, r'(^|\s|\b)(\#2|two)($|\s|\b)')
        self.assertEqual(inst.suggested_responses, ['#1', '#2'])

        inst = AdditionalKeywordState(user)
        self.assertEqual(len(inst.keyword_responses), 1)
        self.assertEqual(inst.keyword_responses[0].regexp.pattern, r'(^|\s|\b)(\#2|2|second)($|\s|\b)')
        self.assertEqual(inst.keyword_responses[0].order, order + 2)
        self.assertEqual(inst.suggested_responses, ['#2'])

        inst = CapitalizedKeywordState(user)
        self.assertEqual(inst.suggested_responses, ['Yes', 'No'])

        inst = RegExpyKeywordState(user)
        self.assertEqual(inst.suggested_responses, ['\\byolo\\b'])
        self.assertEqual(inst.keyword_responses[0].regexp.pattern, r'(^|\s|\b)(\\byolo\\b)($|\s|\b)')

    def test_keyword_1(self):
        user = StateMachineTestUser(['keyword-state'])
        messages = testing_state_machine.handle_message(user, {'body': '#1'})
        self.assertEqual(messages, [{'body': 'You sent #1!', 'suggestedResponses': ['#1', '#2']}])

        user = StateMachineTestUser(['keyword-state'])
        messages = testing_state_machine.handle_message(user, {'body': 'I want #1!'})
        self.assertEqual(messages, [{'body': 'You sent #1!', 'suggestedResponses': ['#1', '#2']}])

    def test_unmatched(self):
        user = StateMachineTestUser(['keyword-state'])
        messages = testing_state_machine.handle_message(user, {'body': '2'})
        self.assertEqual(messages, [{'body': 'I can\'t handle that message.', 'suggestedResponses': ['#1', '#2']}])

    def test_no_message_body(self):
        user = StateMachineTestUser(['keyword-state'])
        messages = testing_state_machine.handle_message(user, {})
        self.assertEqual(messages, [{'body': 'I can\'t handle that message.', 'suggestedResponses': ['#1', '#2']}])

    def test_no_keywords(self):
        user = StateMachineTestUser(['keywordless-state'])
        messages = testing_state_machine.handle_message(user, {'body': 'Hey dude.'})
        self.assertEqual(messages, [{'body': 'Lol, didn\'t read.'}])

    def test_regexp_keywords(self):
        user = StateMachineTestUser(['regex-state'])
        messages = testing_state_machine.handle_message(user, {'body': 'yolo'})
        self.assertEqual(messages, [{'body': 'nope', 'suggestedResponses': ['\\byolo\\b']}])
        messages = testing_state_machine.handle_message(user, {'body': '\\byolo\\b'})
        self.assertEqual(messages, [{'body': 'yolo', 'suggestedResponses': ['\\byolo\\b']}])
        messages = testing_state_machine.handle_message(user, {'body': '\\byolo\\byolo'})
        self.assertEqual(messages, [{'body': 'nope', 'suggestedResponses': ['\\byolo\\b']}])
