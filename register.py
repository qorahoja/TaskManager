from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlcommands import TaskManagerDB
from KeyboardButtons import get_main_menu_keyboard
from states import RegistrationStates

async def start_registration(message: types.Message):
    await message.reply("Welcome! Please enter your username:")
    await RegistrationStates.waiting_for_username.set()

async def process_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.reply("Now, please enter your password:")
    await RegistrationStates.waiting_for_password.set()

async def process_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    username = user_data['username']
    password = message.text
    user_id = message.from_user.id

    db = TaskManagerDB()
    if db.register_user(user_id, username, password):
        await message.reply("Registration successful!\n")
        await message.reply("Welcome to your dashboard!", reply_markup=get_main_menu_keyboard())
    else:
        await message.reply("User already exists. Please try again.")
    
    await state.finish()
    db.close()
