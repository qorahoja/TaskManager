from aiogram.dispatcher.filters.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

class LoginStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

class NewGroupStates(StatesGroup):
    waiting_for_group_name = State()

class SettingsStates(StatesGroup):
    waiting_for_setting = State()
    waiting_for_new_username = State()
    waiting_for_new_password = State()