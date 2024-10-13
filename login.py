from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlcommands import TaskManagerDB
from KeyboardButtons import get_main_menu_keyboard
from states import LoginStates


async def start_login(message: types.Message):
    await message.reply("Please enter your username:")
    await LoginStates.waiting_for_username.set()

async def process_username(message: types.Message, state: FSMContext):
    username = message.text
    user_id = message.from_user.id

    db = TaskManagerDB()
    user = db.get_user(user_id)

    if user and user[1] == username:
        await message.reply("Please enter your password:")
        await state.update_data(user_id=user_id)
        await LoginStates.waiting_for_password.set()
    else:
        await message.reply("User not found. Please register first.")
        await state.finish()
        db.close()
        return

async def check_password(message: types.Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    user_id = user_data['user_id']

    db = TaskManagerDB()
    user = db.get_user(user_id)

    if user and user[2] == password:
     
        await message.reply("Login successful!\n")
        await message.reply("Welcome to your dashboard!", reply_markup=get_main_menu_keyboard())
    else:
        await message.reply("Incorrect password. Please try again.")

    await state.finish()
    db.close()

