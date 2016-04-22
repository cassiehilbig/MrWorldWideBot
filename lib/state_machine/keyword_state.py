import re

from state import State
from kik.messages.responses import TextResponse
from lib.message_types import MessageType

order = 1


class KeywordResponder(object):
    def __init__(self, fn, keyword, *alternates):
        global order
        self.fn = fn
        self.keyword = keyword

        # Create a regexp that has each of the tests for these words in a group with word boundaries. Drop all word-
        # boundary characters from the matchable list.
        words = [keyword] + list(alternates)
        escaped_words = (re.escape(w) for w in words)
        self.regexp = re.compile(unicode(r'(^|\s|\b)({})($|\s|\b)').format('|'.join(escaped_words)), flags=re.I)
        self.order = order
        order += 1

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def match(self, body):
        if not body:
            return False
        return self.regexp.search(body)


def keyword_response(keyword, *alternates):
    def wrap(func):
        return KeywordResponder(func, keyword, *alternates)

    return wrap


class KeywordState(State):
    @staticmethod
    def type():
        raise NotImplementedError('KeywordState is an abstract class and should not be directly used')

    def __init__(self, *args, **kwargs):
        super(KeywordState, self).__init__(*args, **kwargs)
        self.keyword_responses = []
        self.hide_keyboard = False

        # Have to climb the inheritance hierarchy for the instance to make sure we get all keyword responses.
        inspect_class = self.__class__
        while not inspect_class == object:
            for x, y in inspect_class.__dict__.items():
                if isinstance(y, KeywordResponder):
                    self.keyword_responses.append(y)
            inspect_class = inspect_class.__bases__[0]

        self.keyword_responses.sort(key=lambda sr: sr.order)
        if len(self.keyword_responses) <= 20:
            self.suggested_responses = [TextResponse(body=kw.keyword)for kw in self.keyword_responses]
        else:
            self.suggested_responses = None

    def on_message(self, message):
        transition = None
        for sr in self.keyword_responses:
            if message.type == MessageType.TEXT and sr.match(message.body):
                transition = sr(self, message)
                break
        if not transition:
            transition = self.handle_unmatched(message)
        return transition

    def handle_unmatched(self, message):
        """
        Method that subclasses must implement in order to respond to messages that do not match the state's suggested
        responses list.
        :param message: The incoming message.
        :return: A Transition entity
        """
        raise NotImplementedError('KeywordState must return a Transition entity from its `handle_unmatched` method')
