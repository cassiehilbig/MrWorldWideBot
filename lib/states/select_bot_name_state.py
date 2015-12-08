from const import MessageType
from lib.kik_bot import make_text_message
from lib.state_machine import KeywordState, keyword_response, PopTransition, LambdaTransition


class SelectBotNameStateStrings(object):
    NO_BOT_FOUND_TEXT = 'I don\'t think that\'s a bot you own. Try again?'
    MORE_RESPONSE_TEXT = 'How about one of these?'
    UNKNOWN_MESSAGE_TYPE_TEXT = 'I\m sorry, I don\'t understand that message. Please send a text message'


class SelectBotNameState(KeywordState):
    """
    This is a sort of dynamic keyword type state that will allow users to cycle through lists of their bot user names
    """
    def get_suggested_responses(self):
        user_state_data = self.user.current_state_data()
        offset = user_state_data.get('offset', 0)
        user_bots = sorted(self.user.bots())
        if offset >= len(user_bots):
            offset = 0
            user_state_data['offset'] = 0
        if len(user_bots) - offset > 6 or len(user_bots) > 6:
            suggested_responses = user_bots[offset:offset + 5] + ['More', 'Cancel']
        else:
            suggested_responses = user_bots[offset:offset + 6] + ['Cancel']
        return suggested_responses

    @keyword_response('More', 'next')
    def on_more_message(self, message):
        user_state_data = self.user.current_state_data()
        user_state_data['offset'] = user_state_data.get('offset', 0) + 5
        return LambdaTransition([make_text_message(
            SelectBotNameStateStrings.MORE_RESPONSE_TEXT,
            self.user.id,
            suggested_responses=self.get_suggested_responses()
        )])

    @keyword_response('Cancel', 'abort', 'stop', 'quit')
    def on_cancel_message(self, message):
        self._clear_bot_name_offset()
        return PopTransition([])

    def handle_unmatched(self, message):
        if message['type'] == MessageType.TEXT:
            lower_body = message['body'].lower()
            user_bots = self.user.bots()
            if lower_body in user_bots:
                self._clear_bot_name_offset()
                return self.on_bot_name_message(message)
            else:
                return LambdaTransition([make_text_message(
                    SelectBotNameStateStrings.NO_BOT_FOUND_TEXT,
                    self.user.id,
                    suggested_responses=self.get_suggested_responses()
                )])
        else:
            return LambdaTransition([make_text_message(
                SelectBotNameStateStrings.UNKNOWN_MESSAGE_TYPE_TEXT,
                self.user.id,
                suggested_responses=self.get_suggested_responses()
            )])

    def on_bot_name_message(self, message):
        raise NotImplementedError('SelectBotNameState must implement `on_bot_name_message` and return a Transition.')

    def _clear_bot_name_offset(self):
        state_data = self.user.current_state_data()
        if 'offset' in state_data:
            del state_data['offset']
