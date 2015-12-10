from state_machine import StateMachine
from states import DefaultState, MenuState, ChooseColorState, ConfirmColorState

state_machine = StateMachine(DefaultState)

state_machine.register_state(MenuState)
state_machine.register_state(ChooseColorState)
state_machine.register_state(ConfirmColorState)
