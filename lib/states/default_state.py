from lib.state_machine import KeywordState, keyword_response, LambdaTransition
from lib.kik_bot import make_text_message


class DefaultStateStrings(object):
    COLOR_MESSAGE = 'Okay, so what is your favorite color?'
    CONFUSED_MESSAGE = 'Sorry what would you like to do?'
    RESUME_MESSAGE = 'What would you like to do now?'


class DefaultState(KeywordState):

    @staticmethod
    def type():
        return 'default'

    @keyword_response('Color', 'colour')
    def handle_color(self, message):
        return LambdaTransition([make_text_message(self.user.id, DefaultStateStrings.COLOR_MESSAGE)])

    def handle_unmatched(self, message):
        return LambdaTransition([make_text_message(self.user.id, DefaultStateStrings.CONFUSED_MESSAGE)])

    def on_resume(self):
        return LambdaTransition([make_text_message(self.user.id, DefaultStateStrings.RESUME_MESSAGE)])
