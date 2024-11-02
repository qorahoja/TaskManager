from aiogram.dispatcher import FSMContext
from aiogram import types
from states import NewTaskStates
from sqlcommands import TaskManagerDB
from aiogram.types import CallbackQuery
from InlineButtons import create_member_for_role  # Assuming this generates inline buttons
from datetime import datetime

# Get the current date

db = TaskManagerDB()
selected_members = {}  # Temporarily stores selected members by user ID

async def start_task_creation(message: types.Message):
    await message.answer("Please provide the task name:")
    await NewTaskStates.waiting_for_task_name.set()

async def process_task_name(message: types.Message, state: FSMContext):
    await state.update_data(task_name=message.text)
    await message.answer("Please provide the task description:")
    await NewTaskStates.waiting_for_task_description.set()

async def process_task_description(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    group_name = db.get_group_name_by_id(user_id)

    if not group_name:
        await message.answer("You are not a member of any group.")
        return

    members = db.get_members(group_name['group_name'])
    if not members:
        await message.answer(f"No members found in the group '{group_name['group_name']}'.")
        return

    selected_members[user_id] = []  # Initialize selected members for this task
    await show_member_selection(message, members, state)

async def show_member_selection(message: types.Message, members, state: FSMContext):
    data = await state.get_data()
    selected_member_ids = {member['member_id'] for member in data.get('selected_members', []) if 'member_id' in member}

    # Standardize `members` as a list of dictionaries regardless of initial structure
    unassigned_members = [
        {'member_id': member[0], 'name': member[1]} if isinstance(member, tuple) else member
        for member in members
        if (member[0] if isinstance(member, tuple) else member['member_id']) not in selected_member_ids
    ]

    if unassigned_members:
        markup = create_member_for_role(unassigned_members)
        await message.answer("Select a member for the role", reply_markup=markup)
        await NewTaskStates.waiting_for_member.set()
    else:
        await message.answer("All members have been assigned.")
        await state.finish()


async def member_selected(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    member_id = callback_query.data.split("_")[-1]  # Extract member_id from callback data

    selected_members.setdefault(user_id, []).append({'member_id': member_id})
    await state.update_data(selected_members=selected_members[user_id], current_role=None)

    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer("What is this member's role?")
    await NewTaskStates.waiting_for_role.set()

async def process_role(message: types.Message, state: FSMContext):
    role = message.text
    await state.update_data(role=role)

    await message.answer("Please provide a brief description of the work to be done.")
    await NewTaskStates.waiting_for_task_summary.set()

async def process_task_summary(message: types.Message, state: FSMContext):
    await state.update_data(task_summary=message.text)
    await message.answer("Enter a deadline in days (e.g., 3):")
    await NewTaskStates.waiting_for_deadline.set()

async def process_deadline(message: types.Message, state: FSMContext):
    from bot import bot
    deadline = int(message.text)
    user_data = await state.get_data()
    user_id = message.from_user.id

    # Initialize selected_members for this user if it doesn't exist
    if user_id not in selected_members:
        selected_members[user_id] = []

    # Ensure that selected_members only contains dictionaries with task details
    if isinstance(user_data['selected_members'][-1], str):  # Check if last entry is a plain ID
        member_id = user_data['selected_members'].pop()  # Remove the ID from selected_members
    else:
        member_id = user_data['selected_members'][-1]['member_id']  # Get member_id if already a dict

    # Create task dictionary and append to selected_members
    task_data = {
        "member_id": member_id,
        "role": user_data['role'],
        "task_summary": user_data['task_summary'],
        "deadline": deadline
    }
    selected_members[user_id].append(task_data)  # Add task_data to selected_members
   
    # Refresh members list, excluding assigned ones
    group_name = db.get_group_name_by_id(message.from_user.id)
    all_members = db.get_members(group_name['group_name'])
    
    # Filter out assigned members by checking the appropriate index for member IDs in tuples or dictionaries
    assigned_member_ids = {member['member_id'] for member in selected_members[user_id] if isinstance(member, dict)}
    remaining_members = [
        m for m in all_members if (m[0] if isinstance(m, tuple) else m['member_id']) not in assigned_member_ids
    ]

    # Show remaining members or finish if all assigned
    if remaining_members:
        await show_member_selection(message, remaining_members, state)
        real_member_info = next((m for m in all_members if m[0] == member_id), None)
        current_date = datetime.now()

    # Format the date to 'YYYY-MM-DD'
        formatted_date = current_date.strftime("%Y-%m-%d")
        if real_member_info:
            real_member_id = real_member_info[0]  # e.g., 'bb'
            user_name = real_member_info[1]  # e.g., 2
            # Send a message to the user about the new task
            await bot.send_message(chat_id=user_id, text=f"You have a new task:\n\n{task_data['task_summary']}\n\nDeadline: {task_data['deadline']} days")
            db.save_task_to_db(
                user_name, real_member_id, group_name['group_name'], 
                'Assigned', task_data["task_summary"], task_data['deadline'],
                formatted_date
            )
    else:
        await message.answer("All members have been assigned.")


        real_member_info = next((m for m in all_members if m[0] == member_id), None)
        
        
        if real_member_info:
            real_member_id = real_member_info[0]  # e.g., 'bb'
            user_name = real_member_info[1]  # e.g., 2
            
            

            # Save the task in the database
            db.save_task_to_db(
                real_member_id, user_name, group_name['group_name'], 
                'Assigned', task_data["task_summary"], task_data['deadline']
            )

            
    await state.finish()



async def done_assigning(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Task assignment completed.")
    await state.finish()

def register_task_creation_handlers(dp):
    dp.register_message_handler(start_task_creation, lambda message: message.text == "Create Task")
    dp.register_message_handler(process_task_name, state=NewTaskStates.waiting_for_task_name)
    dp.register_message_handler(process_task_description, state=NewTaskStates.waiting_for_task_description)
    dp.register_message_handler(process_role, state=NewTaskStates.waiting_for_role)
    dp.register_message_handler(process_task_summary, state=NewTaskStates.waiting_for_task_summary)
    dp.register_message_handler(process_deadline, state=NewTaskStates.waiting_for_deadline)
    dp.register_callback_query_handler(member_selected, lambda c: c.data.startswith("member_role_"), state=NewTaskStates.waiting_for_member)
    dp.register_callback_query_handler(done_assigning, lambda c: c.data == "done_selection", state=NewTaskStates.waiting_for_member)
