from state_machine import StateMachine
from states import DefaultState, MenuState, ChooseColorState, ConfirmColorState, picture_interceptor, SentPictureState

state_machine = StateMachine(DefaultState)

state_machine.register_global_interceptor(picture_interceptor)

state_machine.register_state(MenuState)
state_machine.register_state(ChooseColorState)
state_machine.register_state(ConfirmColorState)
state_machine.register_state(SentPictureState)
