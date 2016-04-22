from kik.messages import TextMessage

from lib.state_machine import KeywordState, keyword_response, LambdaTransition, StackTransition
from lib.states.state_types import StateTypes


class MenuStateStrings(object):
    COLOR_MESSAGE = 'Okay, so what is your favorite color?'
    CONFUSED_MESSAGE = 'Sorry what language would you like to translate to?'
    RESUME_MESSAGE = 'What language would you like to translate to??'
    NOTHING_MESSAGE = 'What language would you like to translate to?'
    TRANSLATE_TEXT_MESSAGE = 'What would you like to translate to {0}?'


class MenuState(KeywordState):
    # def __init__(self, user):
    #     self.hide_keyboard = False

    @staticmethod
    def type():
        return StateTypes.MENU

    @keyword_response('Thug', 'gangster', 'rap', 'ratchet')
    def handle_thug(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'thug'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Thug"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('French', 'fr')
    def handle_french(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'fr'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("French"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Spanish', 'es')
    def handle_spanish(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'es'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Spanish"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('German', 'de')
    def handle_german(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'de'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("German"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Mandarin', 'zh')
    def handle_mandarin(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'zh'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Mandarin"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Hindi', 'hi')
    def handle_hindi(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'hi'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Hindi"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Arabic', 'ar')
    def handle_arabic(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'ar'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Arabic"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Portuguese', 'pt')
    def handle_portuguese(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'pt'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Portuguese"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Russian', 'ru')
    def handle_russian(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'ru'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Russian"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Japanese', 'ja')
    def handle_japanese(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'ja'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Japanese"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Vietnamese', 'vi')
    def handle_vietnamese(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'vi'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Vietnamese"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    @keyword_response('Korean', 'ko')
    def handle_korean(self, message):
        state_data = self.user.get_state_data(StateTypes.INPUT_TEXT_TOTRANSLATE)
        state_data['language'] = 'ko'
        return StackTransition(
            [TextMessage(to=self.user.id, body=MenuStateStrings.TRANSLATE_TEXT_MESSAGE.format("Korean"))],
            StateTypes.INPUT_TEXT_TOTRANSLATE
        )

    # @keyword_response('Do nothing', 'nothing')
    # def handle_nothing(self, message):
    #     return StackTransition(
    #         [TextMessage(to=self.user.id, body=MenuStateStrings.NOTHING_MESSAGE)],
    #         StateTypes.INPUT_TEXT_TOTRANSLATE
    #     )
    #     return LambdaTransition([TextMessage(to=self.user.id, body=MenuStateStrings.NOTHING_MESSAGE)])

    def handle_unmatched(self, message):
        return LambdaTransition([TextMessage(to=self.user.id, body=MenuStateStrings.CONFUSED_MESSAGE)])

    def on_resume(self):
        return LambdaTransition([TextMessage(to=self.user.id, body=MenuStateStrings.RESUME_MESSAGE)])
