from lib.state_machine import KeywordState, keyword_response, LambdaTransition, StackTransition
from lib.states.state_types import StateTypes
from lib.kik_bot import make_text_message


class MenuStateStrings(object):
    CREATE_A_BOT = 'What would you like your new bot\'s username to be?'
    UPDATE_PROFILE_PICTURE = 'Which bot would you like to update the Profile Picture for?'
    UPDATE_DISPLAY_NAME = 'Which bot would you like to update the Display Name for?'
    UNKNOWN_RESPONSE = 'I\'m sorry, I don\'t know what that means. Try again?'
    DOCS_RESPONSE = 'Visit engine.kik.com/docs on your desktop to view the API Reference. What would you like to do now?'  # noqa
    RESUME_RESPONSE = 'What may I help you with?'


class MenuState(KeywordState):
    @staticmethod
    def type():
        return StateTypes.MENU

    @keyword_response('Create a Bot', 'create', 'make a bot', 'new bot')
    def create_bot_response(self, message):
        return StackTransition(
            [make_text_message(MenuStateStrings.CREATE_A_BOT, self.user.id)], StateTypes.CREATE_BOT_USERNAME_SELECT
        )

    @keyword_response('Set Profile Pic', 'profile picture', 'pic', 'picture', 'photo')
    def update_picture_response(self, message):
        return StackTransition(
            [make_text_message(MenuStateStrings.UPDATE_PROFILE_PICTURE, self.user.id)],
            StateTypes.UPDATE_BOT_PROFILE_PICTURE_SELECT_BOT
        )

    @keyword_response('Set Display Name', 'name')
    def update_display_name_response(self, message):
        return StackTransition(
            [make_text_message(MenuStateStrings.UPDATE_DISPLAY_NAME, self.user.id)],
            StateTypes.UPDATE_BOT_DISPLAY_NAME_SELECT_BOT
        )

    @keyword_response('Docs', 'documentation', 'api', 'reference')
    def get_docs_response(self, message):
        return LambdaTransition([make_text_message(MenuStateStrings.DOCS_RESPONSE, self.user.id)])

    def handle_unmatched(self, message):
        return LambdaTransition([make_text_message(MenuStateStrings.UNKNOWN_RESPONSE, self.user.id)])

    def on_resume(self):
        return LambdaTransition([make_text_message(MenuStateStrings.RESUME_RESPONSE, self.user.id)])
