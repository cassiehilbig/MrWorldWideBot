from unittest import TestCase
from lib.state_machine import State, ConfirmationState, StateMachine, LambdaTransition, keyword_response


class DefaultState(State):

    @staticmethod
    def type():
        return 'foobar'


class BasicConfirmationState(ConfirmationState):
    @staticmethod
    def type():
        return 'confirmation-state'

    def handle_positive_response(self, message):
        return LambdaTransition([{'body': 'You\'re a great chatter'}])

    def handle_negative_response(self, message):
        return LambdaTransition([{'body': 'I don\'t like you anymore'}])

    def handle_unmatched(self, message):
        return LambdaTransition([{'body': 'Come on now, work with me here'}])


class FancyConfirmationState(BasicConfirmationState):
    @staticmethod
    def type():
        return 'fancy-confirmation-state'

    @keyword_response('Maybe', 'kinda', 'sorta')
    def handle_uncertain_response(self, message):
        return LambdaTransition([{'body': 'Please?'}])


testing_state_machine = StateMachine(DefaultState)

testing_state_machine.register_state(BasicConfirmationState)
testing_state_machine.register_state(FancyConfirmationState)


class StateMachineTestUser(object):
    def __init__(self, states):
        self.states = states


class TestConfirmationState(TestCase):
    def test_creation(self):
        user = StateMachineTestUser([])

        inst = BasicConfirmationState(user)
        self.assertEqual(len(inst.keyword_responses), 2)
        self.assertEqual(inst.suggested_responses, ['Yes', 'No'])

        inst = FancyConfirmationState(user)
        self.assertEqual(len(inst.keyword_responses), 3)
        self.assertEqual(inst.suggested_responses, ['Yes', 'No', 'Maybe'])

    def test_is_abstract(self):
        state = ConfirmationState(StateMachineTestUser([]))
        self.assertRaises(NotImplementedError, state.handle_negative_response, 'lol')
        self.assertRaises(NotImplementedError, state.handle_positive_response, 'lol')
        self.assertRaises(NotImplementedError, state.handle_unmatched, 'lol')
        self.assertRaises(NotImplementedError, state.type)

    def test_positive_response(self):
        user = StateMachineTestUser(['confirmation-state'])
        messages = testing_state_machine.handle_message(user, {'body': 'yeah'})
        self.assertEqual(messages, [{'body': 'You\'re a great chatter', 'suggestedResponses': ['Yes', 'No']}])

    def test_negative_response(self):
        user = StateMachineTestUser(['confirmation-state'])
        messages = testing_state_machine.handle_message(user, {'body': 'nope'})
        self.assertEqual(messages, [{'body': 'I don\'t like you anymore', 'suggestedResponses': ['Yes', 'No']}])

    def test_unmatched(self):
        user = StateMachineTestUser(['confirmation-state'])
        messages = testing_state_machine.handle_message(user, {'body': 'lol you smell'})
        self.assertEqual(messages, [{'body': 'Come on now, work with me here', 'suggestedResponses': ['Yes', 'No']}])

    def test_matches_additional_keywords(self):
        user = StateMachineTestUser(['fancy-confirmation-state'])
        messages = testing_state_machine.handle_message(user, {'body': 'maybe'})
        self.assertEqual(messages, [{'body': 'Please?', 'suggestedResponses': ['Yes', 'No', 'Maybe']}])
