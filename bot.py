from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from sqlcommands import TaskManagerDB
from states import RegistrationStates, LoginStates, NewGroupStates
from register import start_registration, process_username as process_registration_username, process_password as process_registration_password
from login import start_login, process_username as process_login_username, check_password as process_login_password
from newGroup import start_new_group, process_new_group_name

from myGroup import show_my_groups

API_TOKEN = '7079476232:AAFiUAqn3FAVXp4P-m_Uelt4241DtDgOZp8'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Command handlers
@dp.message_handler(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Welcome! Please choose an action:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Login", "Register"))

# Registration handlers
@dp.message_handler(lambda message: message.text == "Register")
async def handle_registration(message: types.Message):
    await start_registration(message)

dp.register_message_handler(process_registration_username, state=RegistrationStates.waiting_for_username)
dp.register_message_handler(process_registration_password, state=RegistrationStates.waiting_for_password)

# Login handlers
@dp.message_handler(lambda message: message.text == "Login")
async def handle_login(message: types.Message):
    await start_login(message)

dp.register_message_handler(process_login_username, state=LoginStates.waiting_for_username)
dp.register_message_handler(process_login_password, state=LoginStates.waiting_for_password)

# New Group handlers
@dp.message_handler(lambda message: message.text == "New Group")
async def handle_new_group(message: types.Message):
    await start_new_group(message)

dp.register_message_handler(process_new_group_name, state=NewGroupStates.waiting_for_group_name)


@dp.message_handler(lambda message: message.text == "My Groups")
async def handle_my_groups(message: types.Message):
    await show_my_groups(message)


@dp.callback_query_handler(lambda c: c.data.startswith("join_group_"))
async def process_group_callback(callback_query: types.CallbackQuery):
    from group import handle_group_selection
    chat_id = callback_query.message.chat.id  # Get the chat ID
    message_id = callback_query.message.message_id  # Get the message ID to delete
    await handle_group_selection(callback_query, chat_id, message_id)



if __name__ == "__main__":
    # Initialize the database
    db = TaskManagerDB()
    executor.start_polling(dp, skip_updates=True)
