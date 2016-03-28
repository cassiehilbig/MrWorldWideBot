from kik.messages.text import TextMessage
from lib.state_machine import KeywordState, keyword_response, LambdaTransition, StackTransition

from lib.states.state_types import StateTypes


class MenuStateStrings(object):
    COLOR_MESSAGE = 'Okay, so what is your favorite color?'
    CONFUSED_MESSAGE = 'Sorry what would you like to do?'
    RESUME_MESSAGE = 'What would you like to do now?'
    NOTHING_MESSAGE = 'Fine I will not do anything.'


class MenuState(KeywordState):

    @staticmethod
    def type():
        return StateTypes.MENU

    @keyword_response('Color', 'colour')
    def handle_color(self, message):
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.COLOR_MESSAGE)],
            StateTypes.CHOOSE_COLOR
        )

    @keyword_response('Do nothing', 'nothing')
    def handle_nothing(self, message):
        return LambdaTransition([TextMessage(to=self.user.id, body=MenuStateStrings.NOTHING_MESSAGE)])

    def handle_unmatched(self, message):
        return LambdaTransition([TextMessage(to=self.user.id, body=MenuStateStrings.CONFUSED_MESSAGE)])

    def on_resume(self):
        return LambdaTransition([TextMessage(to=self.user.id, body=MenuStateStrings.RESUME_MESSAGE)])
