from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from sqlcommands import TaskManagerDB
from states import RegistrationStates, LoginStates, NewGroupStates, SettingsStates
from imports import log, reg, keyButton, InlButt, MyGr, nwGr, setting, state, sqlCommand, addMember, members, action
API_TOKEN = '7079476232:AAFiUAqn3FAVXp4P-m_Uelt4241DtDgOZp8'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    args = message.get_args()
    
    if args:
        shorted_hash = args
        decrypted_group_name = db.decrypt_string(shorted_hash)
        
        if decrypted_group_name:  
            check_user = db.check_user_exists(message.from_user.id)
            
            if check_user:  # User exists
                user_id = check_user[0]  # Assuming the user ID is the first element
                
                if db.is_admin(user_id):  # Now checks if the user is an admin
                    await message.answer(f'You are the admin of this group: {decrypted_group_name}')
                else:
                    await message.answer(f"Welcome to {decrypted_group_name}!")
                    db.add_member_to_group(user_id, message.from_user.first_name, decrypted_group_name)
            else:
                await message.answer("Please register first, then click the link!")
                await reg.start_registration(message)
        else:
            await message.answer("Invalid or expired link.")
    else:
        await message.answer("Welcome to TaskManager! Use the commands to get started.")




# Registration handlers
@dp.message_handler(lambda message: message.text == "Register")
async def handle_registration(message: types.Message):
    await reg.start_registration(message)

dp.register_message_handler(reg.process_username, state=RegistrationStates.waiting_for_username)
dp.register_message_handler(reg.process_password, state=RegistrationStates.waiting_for_password)

# Login handlers
@dp.message_handler(lambda message: message.text == "Login")
async def handle_login(message: types.Message):
    await log.start_login(message)

dp.register_message_handler(log.process_username, state=LoginStates.waiting_for_username)
dp.register_message_handler(log.check_password, state=LoginStates.waiting_for_password)

# New Group handlers
@dp.message_handler(lambda message: message.text == "New Group")
async def handle_new_group(message: types.Message):
    await nwGr.start_new_group(message)

dp.register_message_handler(nwGr.process_new_group_name, state=NewGroupStates.waiting_for_group_name)


@dp.message_handler(lambda message: message.text == "My Groups")
async def handle_my_groups(message: types.Message):
    await MyGr.show_my_groups(message)


@dp.callback_query_handler(lambda c: c.data.startswith("join_group_"))
async def process_group_callback(callback_query: types.CallbackQuery):
    from group import handle_group_selection
    chat_id = callback_query.message.chat.id  # Get the chat ID
    message_id = callback_query.message.message_id  # Get the message ID to delete
    await handle_group_selection(callback_query, chat_id, message_id)

@dp.message_handler(lambda message: message.text == "Settings")
async def handle_settings(message: types.Message):
    await setting.start_settings(message)


@dp.message_handler(state=SettingsStates.waiting_for_setting)
async def handle_setting_action(message: types.Message):
    await setting.process_setting_choice(message, state=SettingsStates.waiting_for_setting)

@dp.message_handler(state=SettingsStates.waiting_for_new_username)
async def handle_update_username(message: types.Message, state: FSMContext):
    await setting.process_new_username(message, state)

@dp.message_handler(state=SettingsStates.waiting_for_new_password)
async def handle_update_password(message: types.Message, state: FSMContext):
    await setting.process_new_password(message, state)



"""Add member block"""


@dp.message_handler(lambda message: message.text == "Add Member")
async def handle_add_message(message: types.Message):
    await addMember.handle_add_member(message, message.from_user.id)


"""Members block and inside actions"""


@dp.message_handler(lambda message: message.text == "Members")
async def handle_members(message: types.Message):
    
    await members.handle_members(message, message.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith("info_"))
async def process_group_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("_")[1]
    await action.handle_action(callback_query.message, user_id)

@dp.callback_query_handler(lambda c: c.data.startswith("remove_user_"))
async def process_removeUser_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("_")[2]
    await action.handle_remove_user(callback_query.message, user_id)

@dp.callback_query_handler(lambda c: c.data.startswith("history_"))
async def process_historyUser_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("_")[1]
    # Processing user history
    print(user_id)
    await action.handle_user_history(callback_query.message, callback_query.from_user.id, user_id)

    # Answering the callback to prevent the loading circle
    await bot.answer_callback_query(callback_query.id, text="Fetching user history...")



if __name__ == "__main__":
    # Initialize the database
    db = TaskManagerDB()
    executor.start_polling(dp, skip_updates=True)
