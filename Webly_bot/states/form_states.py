# form_states.py

from aiogram.fsm.state import StatesGroup, State

class FormStates(StatesGroup):
    waiting_for_callback = State()
    name = State()
    phone = State()
    comment = State()
    message_to_manager = State()

class DialogStates(StatesGroup):
    awaiting_admin_reply = State()


