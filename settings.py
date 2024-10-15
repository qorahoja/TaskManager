from aiogram import types
from aiogram.dispatcher import FSMContext
from states import SettingsStates  # Import the state class you defined in states.py
from sqlcommands import TaskManagerDB  # Assuming your db functions are here
from KeyboardButtons import settings_buttons
# Initialize the database
db = TaskManagerDB()

async def start_settings(message: types.Message):
    markup = settings_buttons()
    await message.answer("What would you like to change?\n1. Change Username\n2. Change Password", reply_markup=markup)
    await SettingsStates.waiting_for_setting.set()  # Set the state for user input


async def process_setting_choice(message: types.Message, state: FSMContext):
    choice = message.text.strip()
    print(choice)
    if choice == "1":
        await message.answer("Please enter your new username:")
        await SettingsStates.waiting_for_new_username.set()  # Set state for new username
    elif choice == "2":
        await message.answer("Please enter your new password:")
        await SettingsStates.waiting_for_new_password.set()  # Set state for new password
    else:
        await message.answer("Invalid choice. Please type '1' for Username or '2' for Password.")

async def process_new_username(message: types.Message, state: FSMContext):
    new_username = message.text.strip()
    user_id = message.from_user.id  # Get the user ID from the message
    db.update_username(user_id, new_username)  # Assuming you have this function in sqlcommands.py
    await message.answer("Username updated successfully!")
    await state.finish()  # Reset the state

async def process_new_password(message: types.Message, state: FSMContext):
    new_password = message.text.strip()
    user_id = message.from_user.id  # Get the user ID from the message
    db.update_password(user_id, new_password)  # Assuming you have this function in sqlcommands.py
    await message.answer("Password updated successfully!")
    await state.finish()  # Reset the state
