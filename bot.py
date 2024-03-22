import logging
from operator import sub
import config
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from states import States
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentTypes
import random
import string
import asyncio
import datetime


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

async def calculate_total_points_and_mark_silver():
    # Connect to the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Retrieve all member_ids and their corresponding total points
    cursor.execute("SELECT worker_id, SUM(point_for_this_task) FROM workers_worked_tasks GROUP BY worker_id")
    results = cursor.fetchall()

    # Update members to mark as silver if total points exceed 20
    for member_id, total_points in results:
        if total_points > 20:
            cursor.execute("UPDATE members SET rank_member = 'silver' WHERE member_id = ?", (member_id,))

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

async def periodic_task(interval):
    while True:
        await calculate_total_points_and_mark_silver()
        await asyncio.sleep(interval)

async def main():
    interval = 20 * 60  # 20 minutes in seconds
    await periodic_task(interval)



# Function to set the deadline in the members table
def set_deadline_in_database(member_id, deadline_time):
    cursor.execute("UPDATE members SET deadline = ?, member_status = ? WHERE member_id = ?", (deadline_time, "active", member_id))
    conn.commit()
    
def set_info_to_workers_worked_tasks(member_id, group_name, point, subject):
    cursor.execute("INSERT INTO workers_worked_tasks (worker_id, group_name, point_for_this_task, task_subject) VALUES (?, ?, ?, ?)", (member_id, group_name, point, subject,))
    conn.commit()
# Function to check if a task deadline has expired
async def check_deadline():
    while True:
        cursor.execute("SELECT member_id, deadline FROM members WHERE deadline IS NOT NULL")
        tasks = cursor.fetchall()
        for member_id, deadline_str in tasks:
            deadline_time = datetime.datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() >= deadline_time:
                await bot.send_message(chat_id=member_id, text="The deadline for your task has expired!")
                # Optionally, you can clear the deadline in the database after it expires
                cursor.execute("UPDATE members SET deadline = NULL WHERE member_id = ?", (member_id,))
                conn.commit()
        # Check every hour
        await asyncio.sleep(3600)



def generate_token(group_name):
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"https://t.me/TaskTrackrBot?start={group_name}_{random_part}".replace(' ', '-')



# Define start command handler
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    if message.get_args():
        group_name = message.get_args().split('_')[0].replace('-', ' ')
        cursor.execute("SELECT group_admin FROM groups WHERE group_name = ?", (group_name,))
        all_admins = cursor.fetchall()
        cursor.execute("SELECT member_id FROM members WHERE group_name = ?", (group_name,))
        member_id = cursor.fetchall()



        for row_admins in all_admins:

            if member_id:
                for mem_id in member_id:
                    if user_id == mem_id[0]:
                        await message.answer("You are already a member of this group")


            if user_id == row_admins[0]:
                await message.answer("You are admin this group")
            else:
                
                member_name  = message.from_user.first_name
                member_id = message.from_user.id
        
                cursor.execute("INSERT INTO members (member_id, member_name, group_name, member_status, rank_member) VALUES (?, ?, ?, ?, ?)", (member_id, member_name, group_name, 'empty', 'bronze'))
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
    remove_markup = types.ReplyKeyboardRemove()
    await message.reply("Please enter your password📟", reply_markup=remove_markup)
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
    remove_markup = types.ReplyKeyboardRemove()

    if existing_user:
        await message.answer("Please enter your password: ", reply_markup=remove_markup)
        await state.set_state(States.login_pass)

    else:
        await message.answer("You are not registered")

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
        my_groups = types.KeyboardButton("My Groups")
        
        keyboard.add(create_grup, settings, my_groups)
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
        my_groups = types.KeyboardButton("My Groups")
        
        keyboard.add(create_grup, settings, my_groups)
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

    cursor.execute("SELECT group_name FROM groups WHERE group_admin = ?", (user_id,))
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
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            register_button = types.KeyboardButton("Register 👥")
            login_button = types.KeyboardButton("Login 👤")
            keyboard.add(register_button, login_button)
            await message.answer("I think you did not remember the name of your group, please try to restore it with your name", reply_markup=keyboard)
            await state.finish()


@dp.message_handler(state=States.new_pass)
async def new_pass(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_pass = message.text

    cursor.execute("UPDATE users SET user_pass = ? WHERE member_id", (new_pass, user_id))

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
    global group_name
    group_name = callback_query.data.split('_')[1]  # Extract the group name from the callback data
    user_id = callback_query.from_user.id
    group.clear()
    group["group_name"] = group_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_member = types.KeyboardButton("Add member ➕")
    members = types.KeyboardButton("Members 🫂")
    create_task = types.KeyboardButton("Create Task")
    history_of_tasks = types.KeyboardButton("History")
    keyboard.add(add_member, members, create_task, history_of_tasks)



    
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


import math
# Define tasks_per_page as a global constant
TASKS_PER_PAGE = 10

@dp.message_handler(lambda message: message.text == "History")
async def history(message: types.Message, state: FSMContext):
    group_name = group["group_name"]
    admin_id = message.from_user.id

    cursor.execute("SELECT COUNT(*) FROM history WHERE group_name = ? AND group_admin_id = ?", (group_name, admin_id,))
    total_tasks = cursor.fetchone()[0]  # Fetch the count of tasks
    
    # Calculate total pages
    total_pages = math.ceil(total_tasks / TASKS_PER_PAGE)

    # Extracting page number from the state
    current_page = 1
    async with state.proxy() as data:
        if "page" in data:
            current_page = data["page"]

    # Querying tasks for the current page
    offset = (current_page - 1) * TASKS_PER_PAGE
    cursor.execute("SELECT task_subject, started, finished FROM history WHERE group_name = ? AND group_admin_id = ? LIMIT ? OFFSET ?", (group_name, admin_id, TASKS_PER_PAGE, offset))
    tasks_history = cursor.fetchall()
    
    response_message = f"Total tasks: {total_tasks}\n\nTask History:\n"
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    task_number = offset + 1
    for task in tasks_history:
        task_subject = task[0]
        started_time_str = task[1]
        finished_time_str = task[2]

        # Convert string representations to datetime objects
        started_time = datetime.datetime.fromisoformat(started_time_str)
        finished_time = datetime.datetime.fromisoformat(finished_time_str)

        # Calculate task duration
        task_duration = finished_time - started_time

        # Format task duration
        formatted_duration = str(task_duration).split('.')[0]  # Extracting hours, minutes, and seconds only

        response_message += f"Task {task_number}: {task_subject}\nDuration: {formatted_duration}\n\n"
        callback_data = f"task_{task_subject}"
        button_text = f"{task_number}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))
        task_number += 1
        

    # Add "Next" button if there are more pages
    if total_pages > current_page:
        keyboard.add(InlineKeyboardButton("Next", callback_data="next_page"))
        
    # Add "Back" button if current page is greater than 1
    if current_page > 1:
        keyboard.add(InlineKeyboardButton("Back", callback_data="back_page"))

    await message.answer(response_message, reply_markup=keyboard)




@dp.callback_query_handler(lambda query: query.data.startswith('task_'))
async def task_h(callback: types.CallbackQuery):
    subject = callback.data.split("_")[1]

    cursor.execute("SELECT worker_id, point_for_this_task FROM workers_worked_tasks WHERE task_subject = ?", (subject,))
    workers = cursor.fetchall()

    keyboard = InlineKeyboardMarkup(row_width=5)

    for worker in workers:
        cursor.execute("SELECT member_name FROM members WHERE member_id = ?", (worker[0],))
        member_names = cursor.fetchall()

        for member in member_names:
            back = InlineKeyboardButton("Back", callback_data='back_to_history')
            keyboard.add(back)
            await callback.message.delete()
            await callback.message.answer(f"The workers involved in this work\n\nName: {member[0]}\n\nPoint for this task: {worker[1]}", reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data.startswith('back_to_history'))
async def back_toHistory(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    group_name = group["group_name"]
    admin_id = call.from_user.id

    cursor.execute("SELECT COUNT(*) FROM history WHERE group_name = ? AND group_admin_id = ?", (group_name, admin_id,))
    total_tasks = cursor.fetchone()[0]  # Fetch the count of tasks
    
    # Calculate total pages
    total_pages = math.ceil(total_tasks / TASKS_PER_PAGE)

    # Extracting page number from the state
    current_page = 1
    async with state.proxy() as data:
        if "page" in data:
            current_page = data["page"]

    # Querying tasks for the current page
    offset = (current_page - 1) * TASKS_PER_PAGE
    cursor.execute("SELECT task_subject, started, finished FROM history WHERE group_name = ? AND group_admin_id = ? LIMIT ? OFFSET ?", (group_name, admin_id, TASKS_PER_PAGE, offset))
    tasks_history = cursor.fetchall()
    
    response_message = f"Total tasks: {total_tasks}\n\nTask History:\n"
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    task_number = offset + 1
    for task in tasks_history:
        task_subject = task[0]
        started_time_str = task[1]
        finished_time_str = task[2]

        # Convert string representations to datetime objects
        started_time = datetime.datetime.fromisoformat(started_time_str)
        finished_time = datetime.datetime.fromisoformat(finished_time_str)

        # Calculate task duration
        task_duration = finished_time - started_time

        # Format task duration
        formatted_duration = str(task_duration).split('.')[0]  # Extracting hours, minutes, and seconds only

        response_message += f"Task {task_number}: {task_subject}\nDuration: {formatted_duration}\n\n"
        callback_data = f"task_{task_subject}"
        button_text = f"{task_number}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))
        task_number += 1
        

    # Add "Next" button if there are more pages
    if total_pages > current_page:
        keyboard.add(InlineKeyboardButton("Next", callback_data="next_page"))
        
    # Add "Back" button if current page is greater than 1
    if current_page > 1:
        keyboard.add(InlineKeyboardButton("Back", callback_data="back_page"))

    await call.message.answer(response_message, reply_markup=keyboard)




@dp.callback_query_handler(lambda call: call.data in ('next_page', 'back_page'))
async def page_navigation(callback: types.CallbackQuery, state: FSMContext):
    admin_id = callback.from_user.id
    task_number = 1
    async with state.proxy() as data:
        current_page = data.get("page", 1)
        if callback.data == 'next_page':
            offset = current_page * TASKS_PER_PAGE
            data["page"] = current_page + 1
        else:  # Handle "Back" button
            offset = (current_page - 2) * TASKS_PER_PAGE
            data["page"] = current_page - 1
        
        cursor.execute("SELECT task_subject, started, finished FROM history WHERE group_name = ? AND group_admin_id = ? LIMIT ? OFFSET ?", (group_name, admin_id, TASKS_PER_PAGE, offset))
        tasks_history = cursor.fetchall()
        
        response_message = "Next Page:\n\n" if callback.data == 'next_page' else "Previous Page:\n\n"
        keyboard = InlineKeyboardMarkup(row_width=5)  # Initialize keyboard for inline buttons
        
        for task in tasks_history:
            task_subject = task[0]
            started_time_str = task[1]
            finished_time_str = task[2]
    
            started_time = datetime.datetime.fromisoformat(started_time_str)
            finished_time = datetime.datetime.fromisoformat(finished_time_str)
    
            task_duration = finished_time - started_time
            formatted_duration = str(task_duration).split('.')[0]
    
            response_message += f"Task: {task_subject}\nDuration: {formatted_duration}\n\n"
            callback_data = f"task_{task_subject}"
            button_text = f"{task_number}"
            task_number += 1
            keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))  # Add button for each task
        
        if current_page > 1:
            keyboard.add(InlineKeyboardButton("Back", callback_data="back_page"))  # Add "Back" button if current page is greater than 1
        
        # Add "Next" button if there are more pages
        total_tasks = cursor.execute("SELECT COUNT(*) FROM history WHERE group_name = ? AND group_admin_id = ?", (group_name, admin_id,)).fetchone()[0]
        total_pages = math.ceil(total_tasks / TASKS_PER_PAGE)
        if current_page < total_pages:
            keyboard.add(InlineKeyboardButton("Next", callback_data="next_page"))
    
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=response_message, reply_markup=keyboard)




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



@dp.message_handler(lambda message: message.text == "Create Task")
async def create_task(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    yes = types.KeyboardButton("Yes")
    no = types.KeyboardButton("No")
    keyboard.add(yes, no)
    await message.answer("Ok you have some Technical task", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Yes")
async def technical_task(message: types.Message, state: FSMContext):
    
    remove_markup = types.ReplyKeyboardRemove()
    await message.answer("Please enter your Technical task", reply_markup=remove_markup)
    await state.set_state(States.technical_task)


@dp.message_handler(lambda message: message.text == "No")
async def no(message: types.Message, state: FSMContext):
    await message.answer("Enter the subject of the task")
    await state.set_state(States.tester)


task = {}

@dp.message_handler(state=States.technical_task)
async def save_task(message: types.Message, state: FSMContext):
    
    task['task'] = message.text
    
    await message.answer("Enter the subject of the task")
    await state.set_state(States.tester)


@dp.message_handler(state=States.tester)
async def tester(message: types.Message, state: FSMContext):
        admin_id = message.from_user.id
        group_name = group["group_name"]
        task['task_subject'] = message.text
        print(message.text)
        cursor.execute("INSERT INTO history (group_name, group_admin_id, task_subject, started) VALUES (?, ?, ?, ?)", (group_name, admin_id, message.text, datetime.datetime.now(),))
        conn.commit()
        cursor.execute("SELECT member_name FROM members WHERE group_name = ? AND member_status = ?", (group_name, "empty",))

        all_grups = cursor.fetchall()
        print(all_grups)

        keyboard = InlineKeyboardMarkup()
        for row in all_grups:
            print(row)
            button = InlineKeyboardButton(text=row[0], callback_data=f"tester_{row[0]}")
            print(button.callback_data)
            keyboard.add(button)
 
        await message.answer("Please select tester:", reply_markup=keyboard)
        await state.finish()
        


@dp.callback_query_handler(lambda query: query.data.startswith('tester_'))
async def send_msg_to_tester(callback: types.CallbackQuery, state: FSMContext):
    global tester_
    task_ = task["task_subject"]
    tester_name = callback.data.split('_')[1]

    cursor.execute("SELECT member_id FROM members WHERE member_name = ?", (tester_name,)) 
    tester_ = cursor.fetchone()
    
    if tester_:
        cursor.execute("UPDATE members SET member_status = ?, deadline = ? WHERE member_name = ?", ("as_TESTER", "Tester", tester_name,))

        conn.commit()
        keyboard_finsh = types.ReplyKeyboardMarkup(resize_keyboard=True)
        finish_button = types.KeyboardButton("Task finish")
        keyboard_finsh.add(finish_button)
        await bot.send_message(chat_id=tester_[0], text=f"You are tester for this task {task_}", reply_markup=keyboard_finsh)
        await callback.message.delete()

        group_name = group["group_name"]
     
        cursor.execute("SELECT member_name FROM members WHERE group_name = ? AND member_status = ?", (group_name, "empty",))
        all_grups = cursor.fetchall()

        keyboard = InlineKeyboardMarkup()
        for row in all_grups:
            button = InlineKeyboardButton(text=row[0], callback_data=f"worker_{row[0]}")
            keyboard.add(button)

        await callback.message.answer("Please select worker:", reply_markup=keyboard)
        await state.finish()
           # Set the next state here
    else:
        print("Tester not found")



@dp.message_handler(lambda message: message.text == 'Task finish')
async def task_finished(message: types.Message, state: FSMContext):
    group_name_tester = group["group_name"]
    subject = task["task_subject"]
    print(group_name_tester)  # Ensure this prints the expected value

    tester_id = message.from_user.id

    cursor.execute("SELECT member_id FROM members WHERE deadline = ? AND group_name = ?", ("Tester", group_name_tester))
    check_tester = cursor.fetchone()

    if check_tester is not None and check_tester[0] == tester_id:
        cursor.execute("SELECT member_status, member_name FROM members WHERE group_name = ? AND member_status = ?", (group_name, 'active'))
        active = cursor.fetchall()
        
        if active:
            for row in active:
                await message.answer(f"We have workers who have not completed their tasks yet\n\nNames {row[1]}")
        else:
            cursor.execute("UPDATE members SET member_status = ?, deadline = NULL WHERE deadline = ?", ("empty", "Tester",))
            conn.commit()
            cursor.execute("UPDATE history SET finished = ? WHERE group_name = ? AND task_subject = ?", (datetime.datetime.now(), group_name, subject,))
            conn.commit()
            await message.answer("Task finished")
            
    else:
        await message.answer("You are not assigned as a tester for this group.")




async def start_deadline_checking():
    await check_deadline()




@dp.message_handler(state=States.deadline)
async def deadline(message: types.Message, state: FSMContext):
    try:
        group_name = group["group_name"]
  
        global deadline_time

        # Extract worker details and deadline from the message
        task_ = task['task']
        task_to_employe = task[f'employe_to_{worker_name}']
        deadline_str = message.text
        deadline_datetime = datetime.datetime.strptime(deadline_str, '%y-%m-%d-%H')
        deadline_time = deadline_datetime.strftime('%Y-%m-%d %H:%M:%S')

        if task_: 
            # Set the deadline for the current worker
            cursor.execute("SELECT member_id FROM members WHERE member_name = ? AND member_status = ?", (worker_name, "empty"))
            worker_id = cursor.fetchone() 
            set_deadline_in_database(worker_id[0], deadline_time)

            # Send task details to the current worker
            await bot.send_message(chat_id=worker_id[0], text=f"Technical task: {task_}\n\nYour task: {task_to_employe}\n\nDeadline: {deadline_time}")

            # Check if there are more empty workers available
            cursor.execute("SELECT member_id FROM members WHERE member_status = ?", ("empty",))
            next_worker = cursor.fetchone()

            if next_worker:
                cursor.execute("SELECT member_name FROM members WHERE group_name = ? AND member_status = ?", (group_name, "empty",))
                all_grups = cursor.fetchall()

                keyboard = InlineKeyboardMarkup()
                for row in all_grups:
                    button = InlineKeyboardButton(text=row[0], callback_data=f"worker_{row[0]}")
                    keyboard.add(button)
                # If there are more empty workers, select the next worker
                await message.answer("Please select next worker:", reply_markup=keyboard)
                await state.finish()
                
            else:
                # If all workers are assigned tasks, consider the task as created
                await message.answer("All workers are assigned tasks. Task created.")
                await state.finish()
        else:
            await message.answer("Task details are missing.")
            await state.finish()

        # Send the message about the deadline
        await message.answer(f"Deadline set to: {deadline_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

        # Start checking the deadline
        await asyncio.create_task(start_deadline_checking())

    except ValueError as e:
        print(e)
        await message.answer("Invalid format for the deadline. Please use yy-mm-dd-hh.")

@dp.callback_query_handler(lambda query: query.data.startswith('worker_'))
async def join_group(callback_query: CallbackQuery, state: FSMContext):
    print(callback_query.data)
    global worker_name
    worker_name = callback_query.data.split('_')[1]
    
    await callback_query.message.answer("Please write a task for the employee")

    await state.set_state(States.write_task_for_employe)

@dp.message_handler(state=States.write_task_for_employe)
async def write_employe(message: types.Message, state: FSMContext):
    task[f'employe_to_{worker_name}'] = message.text

    await message.answer(f"Please set a deadline for {worker_name}")
    await state.set_state(States.deadline)

@dp.message_handler(content_types=ContentTypes.DOCUMENT)
async def handle_message(message: types.Message, state: FSMContext):
    group_name = group["group_name"]
    user_id = message.from_user.id
    document = message.document

    # Check if the message is related to a task
    try:
        cursor.execute("SELECT member_id, deadline FROM members WHERE member_id = ? AND deadline IS NOT NULL AND group_name = ?", (user_id, group_name))
        task_info = cursor.fetchone()


        if task_info:
            keyboard = InlineKeyboardMarkup()
            # If the message is related to a task, stop the timer for that task
            cursor.execute("UPDATE members SET deadline = NULL, member_status = ? WHERE member_id = ?", ('empty', user_id,))
            conn.commit()
            await bot.send_message(chat_id=user_id, text="You've interacted with the task. Timer stopped.")
            accept = InlineKeyboardButton(text="Accept", callback_data=f"accept_{user_id}")
            decline = InlineKeyboardButton(text="Decline", callback_data=f"decline_{user_id}")
            keyboard.add(accept, decline)
            # Send the document using its file_id
            await bot.send_document(chat_id=tester_[0], document=document.file_id, reply_markup=keyboard)
            await state.finish()
        else:
            await bot.send_message(chat_id=user_id, text="No task found for you in this group.")
    except Exception as e:
        # Handle exceptions, log errors, or notify administrators
        print(f"An error occurred: {e}")


@dp.callback_query_handler(lambda query: query.data.startswith('accept_'), state="*")
async def accept(query: types.CallbackQuery, state: FSMContext):
    print("Hasd")
    global idx
    await query.message.answer("Please rate the employee's performance from 1 to 10")
    await state.set_state(States.point)
    idx = query.data.split('_')[1]
    await query.message.delete()

    await bot.send_message(chat_id=idx, text="Your work has been successfully verified")


@dp.message_handler(state=States.point)
async def point(message: types.Message, state: FSMContext):
    subject = task["task_subject"]
    print(subject)
    group__ = group["group_name"]
    point = message.text
    id = idx

    await message.answer("Thanks for checking")

    set_info_to_workers_worked_tasks(id, group__, point, subject)
    await state.finish()



@dp.callback_query_handler(lambda query: query.data.startswith('decline_'), state="*")
async def decline(query: types.CallbackQuery, state: FSMContext):
    global idx
    await query.message.answer("Please provide information about the detected error")
    idx = query.data.split('_')[1]

    await state.set_state(States.decline)

@dp.message_handler(state=States.decline)
async def decline_message(message: types.Message, state: FSMContext):
    information = message.text
    user_id = message.from_user.id
    await bot.send_message(chat_id=idx, text=f"Task declined.\n\nReason: {information}.")
    await bot.send_message(chat_id=idx, text="Please proceed with the task again.")

    # Reset the deadline for the task
    cursor.execute("UPDATE members SET deadline = NULL, member_status = ? WHERE member_id = ?", ('active', idx))
    conn.commit()
    set_deadline_in_database(idx, deadline_time)

    await asyncio.create_task(start_deadline_checking())
    await state.finish()




# Start the bot with the executor   
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    asyncio.run(main())
