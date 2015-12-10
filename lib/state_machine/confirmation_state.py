from keyword_state import KeywordState, keyword_response


class ConfirmationState(KeywordState):
    @staticmethod
    def type():
        raise NotImplementedError('ConfirmationState is an abstract class and should not be directly used')

    def handle_positive_response(self, message):
        """
        Deal with a positive-sounding message that a user has sent to the bot.
        :param message: The actual message object that was sent.
        :return: A Transition entity
        """
        raise NotImplementedError(
            'ConfirmationState must return a Transition entity from its `handle_positive_response` method'
        )

    def handle_negative_response(self, message):
        """
        Deal with a negative-sounding message that a user has sent to the bot.
        :param message: The actual message object that was sent.
        :return: A Transition entity
        """
        raise NotImplementedError(
            'ConfirmationState must return a Transition entity from its `handle_negative_response` method'
        )

    def handle_unmatched(self, message):
        raise NotImplementedError(
            'ConfirmationState must return a Transition entity from its `handle_unmatched` method'
        )

    @keyword_response('Yes', 'yep', 'yea', 'sure', 'ok', 'ya', 'yah', 'yeah', 'y', 'k', 'okay', 'allow')
    def _handle_positive_response(self, message):
        """
        Private method that takes care of the name ignoring of keyword responses.
        """
        return self.handle_positive_response(message)

    @keyword_response('No', 'cancel', 'back', 'n', 'nah', 'deny', 'nope')
    def _handle_negative_response(self, message):
        """
        Private method that takes care of the name ignoring of keyword responses.
        """
        return self.handle_negative_response(message)
