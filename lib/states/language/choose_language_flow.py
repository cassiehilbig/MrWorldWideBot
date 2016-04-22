from kik.messages import TextResponse, TextMessage

from lib.message_types import MessageType
from lib.state_machine import KeywordState, keyword_response, Transition, PopTransition,\
    LambdaTransition
from lib.states.state_types import StateTypes
from lib.states import TranslationState, MenuState
import getTranslation
import gizoogleshit

LANGUAGES = ['French', 'Spanish', 'German', 'Mandarin', 'Hindi', 'Arabic']


class ChooseLanguageStrings(object):

    UNKNOWN_MESSAGE_TYPE = 'Please send me what language you would like to translate to.'
    UNKNOWN_LANGUAGE = 'I don\'t know this language :( Please pick from {}.'.format(', '.join(LANGUAGES))
    NEXT_LANGUAGE = 'What language would you like to translate to?'
    CANCEL_MESSAGE = 'Okay no problem, you can choose one later.'
    NEXT_TRANSLATION = 'What else would you like translated?'
    #CONFIRM_COLOR = 'So your favorite color is {color}?'
    CONFIRMED_LANGUAGE = 'Okay, what would you like to translate to {0}?'
    #CONFIRMATION_CANCELLED = 'Okay, so what is your favorite color then?'
    #CONFIRMATION_CONFUSED = 'So is your favorite color {color} or not?'


class ChooseLanguageState(KeywordState):

    @staticmethod
    def type():
        return StateTypes.CHOOSE_LANGUAGE

    def __init__(self, user):
        super(ChooseLanguageState, self).__init__(user)

        # We don't want to have too many functions, so let's add suggested responses dynamically
        #self.suggested_responses = [TextResponse(body=x) for x in LANGUAGES] + self.suggested_responses

    # @keyword_response('Cancel', 'back')
    # def handle_cancel(self, message):
    #     return PopTransition([TextMessage(to=self.user.id, body=ChooseFavoriteColorStrings.CANCEL_MESSAGE)])

    def handle_unmatched(self, message):
        if message.type != MessageType.TEXT:
            return LambdaTransition([TextMessage(to=self.user.id,
                                                 body=ChooseLanguageStrings.UNKNOWN_MESSAGE_TYPE)])

        lower_langs = [c.lower() for c in LANGUAGES]
        pick = message.body.strip().lower()

        if pick not in lower_langs:
            return LambdaTransition([TextMessage(to=self.user.id, body=ChooseLanguageStrings.UNKNOWN_LANGUAGE)])

        self.user.get_state_data(TranslateLanguageState.type())['language'] = pick

        msg = ChooseLanguageStrings.CONFIRMED_LANGUAGE.format(language=pick)
        return Transition([TextMessage(to=self.user.id, body=msg)], TranslateLanguageState.type())

    def on_resume(self):
        return LambdaTransition([TextMessage(to=self.user.id, body=ChooseLanguageStrings.UNKNOWN_MESSAGE_TYPE)])


class TranslateLanguageState(TranslationState):
    def __init__(self, user):
        super(TranslateLanguageState, self).__init__(user)
        self.hide_keyboard = True

    @staticmethod
    def type():
        return StateTypes.INPUT_TEXT_TOTRANSLATE
    #
    # def handle_french_response(self, message):
    #     language = self.user.current_state_data()['language']
    #
    #     self.user.clear_current_state_data()
    #     m = getTranslation(language, message.body)
    #     # m = ChooseFavoriteColorStrings.CONFIRMED_COLOR.format(color=color)
    #     return PopTransition([TextMessage(to=self.user.id, body=m)])
    #
    # def handle_spanish_response(self, message):
    #     self.user.clear_current_state_data()
    #     m = "spanish bish"
    #     return Transition([
    #         TextMessage(to=self.user.id, body=m)], ChooseLanguageState.type()
    #         # TextMessage(to=self.user.id, body=ChooseFavoriteColorStrings.CONFIRMATION_CANCELLED)],
    #         # ChooseColorState.type()
    #     )
    #
    # def handle_german_response(self, message):
    #     self.user.clear_current_state_data()
    #     m = "german bish"
    #     return Transition([
    #         TextMessage(to=self.user.id, body=m)], ChooseLanguageState.type()
    #         # TextMessage(to=self.user.id, body=ChooseFavoriteColorStrings.CONFIRMATION_CANCELLED)],
    #         # ChooseColorState.type()
    #     )

    @keyword_response("Change Language")
    def handle_language_change(self, message):
        return Transition([TextMessage(to=self.user.id, body=ChooseLanguageStrings.NEXT_LANGUAGE)], MenuState.type())

    def handle_unmatched(self, message):
        language = self.user.current_state_data()['language']
        if language == "thug":
            m = gizoogleshit.gizoogleit(message.body)
        else:
            m = getTranslation.translateshit(language, message.body)
        # color = self.user.current_state_data()['color']
        #m = ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color=color)

        return LambdaTransition([
            TextMessage(to=self.user.id, body=m), TextMessage(to=self.user.id, body=ChooseLanguageStrings.NEXT_TRANSLATION)]
        )

    def on_resume(self):
        color = self.user.current_state_data()['color']
        #m = ChooseFavoriteColorStrings.CONFIRMATION_CONFUSED.format(color=color)
        m = 'gurl whatttt'
        return LambdaTransition([TextMessage(to=self.user.id, body=m)])
