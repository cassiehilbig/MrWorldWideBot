from lib.state_machine import KeywordState, keyword_response, LambdaTransition
from lib.kik_bot import make_text_message


class MenuStateStrings(object):
    COLOR_MESSAGE = 'Okay, so what is your favorite color?'
    CONFUSED_MESSAGE = 'Sorry what would you like to do?'
    RESUME_MESSAGE = 'What would you like to do now?'
    NOTHING_MESSAGE = 'Fine I will not do anything.'


class MenuState(KeywordState):

    @staticmethod
    def type():
        return 'menu'

    @keyword_response('Color', 'colour')
    def handle_color(self, message):
        return LambdaTransition([make_text_message(MenuStateStrings.COLOR_MESSAGE, self.user.id)])

    @keyword_response('Do nothing', 'nothing')
    def handle_nothing(self, message):
        return LambdaTransition([make_text_message(MenuStateStrings.NOTHING_MESSAGE, self.user.id)])

    def handle_unmatched(self, message):
        return LambdaTransition([make_text_message(MenuStateStrings.CONFUSED_MESSAGE, self.user.id)])

    def on_resume(self):
        return LambdaTransition([make_text_message(MenuStateStrings.RESUME_MESSAGE, self.user.id)])
