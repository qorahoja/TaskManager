import logging
import config
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from states import States
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random
import string


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
API_TOKEN = config.BOT_API  # Replace with your actual Telegram API token
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

group = {}
# Connect to the database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()




def generate_token(group_name):
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"https://t.me/TaskTrackrBot?start={group_name}_{random_part}"



# Define start command handler
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    if message.get_args():
        cursor.execute("SELECT group_admin FROM groups")
        all_admins = cursor.fetchall()
        for row_admins in all_admins:
            if user_id == row_admins[0]:
                await message.answer("You are admin this group")
            else:
                group_name = message.get_args().split('_')[0]
                member_name  = message.from_user.first_name
                member_id = message.from_user.id
        
                cursor.execute("INSERT INTO members (member_id, member_name, group_name) VALUES (?, ?, ?)", (member_id, member_name, group_name,))
                conn.commit()

        await message.answer(f"Welcome new member you have to joined to {group_name}")
    else:
        user_name = message.from_user.first_name

        # Create keyboard with buttons
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        register_button = types.KeyboardButton("Register 👥")
        login_button = types.KeyboardButton("Login 👤")
        
        keyboard.add(register_button, login_button)

        await message.answer(
            f"Welcome <b>{user_name}</b> to the Task Management Bot! 🤖. If you don't have an account, please register!",
            parse_mode=types.ParseMode.HTML,
            reply_markup=keyboard
        )




# Register section
@dp.message_handler(lambda message: message.text == "Register 👥")
async def register(message: types.Message, state: FSMContext):
    print("Register command received")
    remove_markup = types.ReplyKeyboardRemove()
    user_id = message.from_user.id

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await message.answer("You are already registered. Please log in.")
    else:
        await message.answer("Please enter your name 🧑‍💻", reply_markup=remove_markup)
        await state.set_state(States.name)

# Name message handler
@dp.message_handler(state=States.name)
async def name(message: types.Message, state: FSMContext):
    await message.reply("Please enter your password📟")
    await state.update_data(name=message.text)
    await States.next()

# Password message handler
@dp.message_handler(state=States.password)
async def password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = message.from_user.id
        name = data['name']
        password = message.text

    try:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        create_grup = types.KeyboardButton("Create group 👥")
        settings = types.KeyboardButton("Settings ⚙")
        my_groups = types.KeyboardButton("My Groups")
        
        keyboard.add(create_grup, settings, my_groups)
        cursor.execute("INSERT INTO users (user_id, user_name, user_pass) VALUES (?, ?, ?)", (user_id, name, password,))
        conn.commit()
        await message.answer("Registration successful! 👍", reply_markup=keyboard)
        
    except sqlite3.Error as e:
        await message.answer(f"Registration failed. Error: {e}")

    await state.finish()

#Login section

@dp.message_handler(lambda message: message.text == "Login 👤")
async def login(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await message.answer("Please enter your password: ")
        await state.set_state(States.login_pass)

@dp.message_handler(state=States.login_pass)
async def login_pass(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT user_pass FROM users WHERE user_id = ?", (user_id,))
    password = cursor.fetchone()
    if message.text == password[0]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        create_grup = types.KeyboardButton("Create group 👥")
        settings = types.KeyboardButton("Settings ⚙")
        my_groups = types.KeyboardButton("My Groups")
        
        keyboard.add(create_grup, settings, my_groups)
        await message.answer("Welcome Back!", reply_markup=keyboard)
        await state.finish()
    else:
        await message.answer("Please try again")
        await state.set_state(States.try_1)



@dp.message_handler(state=States.try_1)
async def login_pass(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT user_pass FROM users WHERE user_id = ?", (user_id,))
    password = cursor.fetchone()
    if message.text == password[0]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        create_grup = types.KeyboardButton("Create group 👥")
        settings = types.KeyboardButton("Settings ⚙")
        
        keyboard.add(create_grup, settings)
        await message.answer("Welcome Back!", reply_markup=keyboard)
        await state.finish()
    else:
        await message.answer("Please try again")
        await state.set_state(States.try_2)


@dp.message_handler(state=States.try_2)
async def login_pass(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT user_pass FROM users WHERE user_id = ?", (user_id,))
    password = cursor.fetchone()
    if message.text == password[0]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        create_grup = types.KeyboardButton("Create grup 👥")
        settings = types.KeyboardButton("Settings ⚙")
        
        keyboard.add(create_grup, settings)
        await message.answer("Welcome Back!", reply_markup=keyboard)
        await state.finish()
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        yes = types.KeyboardButton("Yes 🔏")
        no = types.KeyboardButton("No 🚫")
        
        
        keyboard.add(yes, no)
        await message.answer("You typed your password 3 times wrong Do you want to reset your password?", reply_markup=keyboard)
        await state.finish()

@dp.message_handler(lambda message: message.text == 'Yes 🔏')
async def reset_password(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT group_admin FROM groups WHERE group_admin = ?", (user_id,))
    group_admin = cursor.fetchone()

    if group_admin and group_admin[0] == user_id:
        print(f"Same: {group_admin[0]} - {user_id}")
        await message.answer("Please enter the name of your group")
        await state.set_state(States.group_name_for_reset)
    else:
        print(f"Not same: {group_admin[0]} - {user_id}")
        await message.answer("You are not a group admin. Please enter your old name.")
        await state.set_state(States.old_name_for_reset)




@dp.message_handler(state=States.group_name_for_reset)
async def reset_with_group_name(message: types.Message, state: FSMContext):
    group_name = message.text
    user_id = message.from_user.id

    cursor.execute("SELECT group_name FROM groups WHERE group_admin = ?", (user_id))
    correct_group_name = cursor.fetchall()

    for all_grup_names in correct_group_name:
        if all_grup_names[0] in group_name:
            await message.answer("Ok please enter your new password")
            await state.set_state(States.new_pass)

        else:
            await message.answer("Invalid group name, please try again")
            await state.set_state(States.try_group_1)

@dp.message_handler(state=States.try_group_1)
async def reset_with_group_name(message: types.Message, state: FSMContext):
    group_name = message.text
    user_id = message.from_user.id

    cursor.execute("SELECT group_name FROM groups WHERE group_admin = ?", (user_id))
    correct_group_name = cursor.fetchall()

    for all_grup_names in correct_group_name:
        if all_grup_names[0] in group_name:
            await message.answer("Ok please enter your new password")
            await state.set_state(States.new_pass)

        else:
            await message.answer("Invalid group name, please try again")
            await state.set_state(States.try_group_2)


@dp.message_handler(state=States.try_group_2)
async def reset_with_group_name(message: types.Message, state: FSMContext):
    group_name = message.text
    user_id = message.from_user.id

    cursor.execute("SELECT group_name FROM groups WHERE group_admin = ?", (user_id))
    correct_group_name = cursor.fetchall()

    for all_grup_names in correct_group_name:
        if all_grup_names[0] in group_name:
            await message.answer("Ok please enter your new password")
            await state.set_state(States.new_pass)


        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            register_button = types.KeyboardButton("Register 👥")
            login_button = types.KeyboardButton("Login 👤")
            keyboard.add(register_button, login_button)
            await message.answer("I think you did not remember the name of your group, please try to restore it with your name", reply_markup=keyboard)
            await state.finish()

@dp.message_handler(state=States.old_name_for_reset)
async def old_name_for_reset(message: types.Message, state: FSMContext):
    print(message.text)
    old_name = message.text
    user_id = message.from_user.id

    cursor.execute("SELECT user_name FROM users WHERE user_id = ?", (user_id,))

    correct_user_name = cursor.fetchone()
    print(correct_user_name[0])
    if old_name == correct_user_name[0]:
        await message.answer("Please enter your new password")
        await state.set_state(States.new_pass)
    else:
        await message.answer("Invalid name")
        await state.finish()


@dp.message_handler(lambda message: message.text == 'No 🚫')
async def no(message: types.Message, state: FSMContext):
    await message.answer("Ok cancled")
    await state.finish()



@dp.message_handler(lambda message: message.text == "Create group 👥")
async def create_group(message: types.Message, state: FSMContext):
        await message.answer("Please enter your team name: ")
        await state.set_state(States.team_name)

@dp.message_handler(state=States.team_name)
async def team_name(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    new_team_name = message.text

    await message.answer(f"New group created. Team name {new_team_name}")

    cursor.execute("INSERT INTO groups (group_name, group_admin) VALUES (?, ?)", (new_team_name, admin_id,))
    conn.commit()
    await state.finish()

@dp.message_handler(lambda message: message.text == 'My Groups')
async def my_groups(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT group_name FROM groups WHERE group_admin = ?", (user_id,))
    all_groups = cursor.fetchall()

    keyboard = InlineKeyboardMarkup()
    for row in all_groups:
        button = InlineKeyboardButton(text=row[0], callback_data=f"group_{row[0]}")
        keyboard.add(button)

    await message.answer("Your groups:", reply_markup=keyboard)




@dp.callback_query_handler(lambda query: query.data.startswith('group_'))
async def join_group(callback_query: CallbackQuery):
    
    group_name = callback_query.data.split('_')[1]  # Extract the group name from the callback data
    user_id = callback_query.from_user.id
    group.clear()
    group["group_name"] = group_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_member = types.KeyboardButton("Add member ➕")
    members = types.KeyboardButton("Members 🫂")
    keyboard.add(add_member, members)

    
    await callback_query.message.delete()
    await callback_query.message.answer(f"You have joined the {group_name} group!", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Add member ➕')
async def add_member(message: types.Message, state: FSMContext):
    group_name = group["group_name"]
    link = generate_token(group_name)

    await message.reply(f"This is a link for people to join your group\n {link}")


@dp.message_handler(lambda message: message.text == "Members 🫂")
async def members(message: types.Message, state: FSMContext):
    group_name = group["group_name"]
    cursor.execute("SELECT member_name FROM members WHERE group_name = ?", (group_name,))
    all_grups = cursor.fetchall()

    keyboard = InlineKeyboardMarkup()
    for row in all_grups:
        button = InlineKeyboardButton(text=row[0], callback_data=f"member_{row[0]}")
        keyboard.add(button)

    await message.answer("Members:", reply_markup=keyboard)

member = {}

@dp.callback_query_handler(lambda query: query.data.startswith('member_'))
async def join_group(callback_query: CallbackQuery):
    
    member_name = callback_query.data.split('_')[1]  # Extract the group name from the callback data
    
    member['name'] = member_name
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    remove_member = types.KeyboardButton("Remove User")
    
    keyboard.add(remove_member)

    
    await callback_query.message.delete()
    await callback_query.message.answer(f"Member name {member_name}", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Remove User")
async def remove_user(message: types.Message, state: FSMContext):
    member_name = member["name"]
    cursor.execute("DELETE FROM members WHERE member_name = ?", (member_name,))
    conn.commit()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_grup = types.KeyboardButton("Create group 👥")
    settings = types.KeyboardButton("Settings ⚙")
    my_groups = types.KeyboardButton("My Groups")
    keyboard.add(create_grup, settings, my_groups)
    await message.answer("Member succesfuly removed!", reply_markup=keyboard)


# Start the bot with the executor   
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
