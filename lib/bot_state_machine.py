from lib.state_machine import StateMachine, PersistenceStrategy

from model.bot_user import BotUser
from states import DefaultState, MenuState, ChooseColorState, ConfirmColorState, picture_interceptor, \
    SentPictureState, GenericState, AlwaysPoppingState, TranslateLanguageState, ChooseLanguageState


class BotUserPersistenceStrategy(PersistenceStrategy):
    def get_or_create(self, entity_name):
        user = BotUser.get_by_id(entity_name)
        return user or BotUser(id=entity_name)

    def get_states(self, entity):
        return entity.states

    def set_states(self, entity, states):
        entity.states = states

    def put(self, entity_name, entity):
        entity.put()

state_machine = StateMachine(DefaultState, BotUserPersistenceStrategy())

state_machine.register_global_interceptor(picture_interceptor)

state_machine.register_state(MenuState)
state_machine.register_state(ChooseColorState)
state_machine.register_state(ConfirmColorState)
state_machine.register_state(SentPictureState)
state_machine.register_state(GenericState)
state_machine.register_state(AlwaysPoppingState)
state_machine.register_state(ChooseLanguageState)
state_machine.register_state(TranslateLanguageState)
