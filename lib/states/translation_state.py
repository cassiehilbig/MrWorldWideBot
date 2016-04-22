from lib.state_machine.keyword_state import KeywordState, keyword_response


class TranslationState(KeywordState):
    @staticmethod
    def type():
        raise NotImplementedError('ConfirmationState is an abstract class and should not be directly used')

    # def handle_french_response(self, message):
    #     """
    #     Deal with a positive-sounding message that a user has sent to the bot.
    #     :param message: The actual message object that was sent.
    #     :return: A Transition entity
    #     """
    #     raise NotImplementedError(
    #         'TranslationState must return a Transition entity from its `handle_french_response` method'
    #     )
    #
    # def handle_spanish_response(self, message):
    #     """
    #     Deal with a negative-sounding message that a user has sent to the bot.
    #     :param message: The actual message object that was sent.
    #     :return: A Transition entity
    #     """
    #     raise NotImplementedError(
    #         'TranslationState must return a Transition entity from its `handle_spanish_response` method'
    #     )
    #
    # def handle_german_response(self, message):
    #     """
    #     Deal with a negative-sounding message that a user has sent to the bot.
    #     :param message: The actual message object that was sent.
    #     :return: A Transition entity
    #     """
    #     raise NotImplementedError(
    #         'TranslationState must return a Transition entity from its `handle_spanish_response` method'
    #     )

    def handle_unmatched(self, message):
        raise NotImplementedError(
            'ConfirmationState must return a Transition entity from its `handle_unmatched` method'
        )

    # @keyword_response('French', 'fr', 'francais')
    # def _handle_french_response(self, message):
    #     """
    #     Private method that takes care of the name ignoring of keyword responses.
    #     """
    #     return self.handle_french_response(message)
    #
    # @keyword_response('Spanish', 'es', 'espanol')
    # def _handle_spanish_response(self, message):
    #     """
    #     Private method that takes care of the name ignoring of keyword responses.
    #     """
    #     return self.handle_spanish_response(message)
    #
    # @keyword_response('German', 'de', 'germ')
    # def _handle_spanish_response(self, message):
    #     """
    #     Private method that takes care of the name ignoring of keyword responses.
    #     """
    #     return self.handle_spanish_response(message)
