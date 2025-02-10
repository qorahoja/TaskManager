from aiogram.dispatcher import FSMContext
from aiogram import types
from states import NewTaskStates
from sqlcommands import TaskManagerDB
from aiogram.types import CallbackQuery
from InlineButtons import create_member_for_role  # Assuming this generates inline buttons
from datetime import datetime
from aiogram import Bot


API_TOKEN = '7079476232:AAFiUAqn3FAVXp4P-m_Uelt4241DtDgOZp8'

bot = Bot(token=API_TOKEN)

# Get the current date

db = TaskManagerDB()
selected_members = {} 
task_data_full = {} # Temporarily stores selected members by user ID

async def start_task_creation(message: types.Message):
    await message.answer("Please provide the task name:")
    await NewTaskStates.waiting_for_task_name.set()

async def process_task_name(message: types.Message, state: FSMContext):
    await state.update_data(task_name=message.text)
    task_data_full['task_name'] = message.text
    await message.answer("Please provide the task description:")
    await NewTaskStates.waiting_for_task_description.set()

async def process_task_description(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    group_name = db.get_group_name_by_id(user_id)
    task_data_full['task_description'] = message.text

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
    selected_member_ids = {member['member_id'] for member in selected_members.get(message.from_user.id, [])}

    # Standardize `members` as a list of dictionaries
    unassigned_members = [
        {'member_id': str(member[0]), 'name': member[1]} if isinstance(member, tuple) else member
        for member in members
        if str(member[0] if isinstance(member, tuple) else member['member_id']) not in selected_member_ids
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
    member_id = callback_query.data.split("_")[-1]  # Extract member_id

    # Ensure selected members list exists
    if user_id not in selected_members:
        selected_members[user_id] = []

    # Prevent duplicate selections
    if any(m['member_id'] == member_id for m in selected_members[user_id]):
        await callback_query.answer("This member is already assigned!", show_alert=True)
        return

    selected_members[user_id].append({'member_id': member_id})  # Append instead of overwrite

    await state.update_data(selected_members=selected_members[user_id])
    task_data_full['selected_members'] = selected_members[user_id]  

    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer("What is this member's role?")
    await NewTaskStates.waiting_for_role.set()




async def process_role(message: types.Message, state: FSMContext):
    role = message.text.strip()
    user_data = await state.get_data()
    user_id = message.from_user.id  # Ensure correct user ID

    if user_id not in selected_members:
        selected_members[user_id] = []

    # Retrieve last assigned member
    member_id = user_data['selected_members'][-1]['member_id']

    group_name = db.get_group_name_by_id(user_id)

    if role.lower() == "tester":  
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Get member details
        all_members = db.get_members(group_name['group_name'])
        real_member_info = next((m for m in all_members if m[0] == member_id), None)

        if real_member_info:
            real_member_id = real_member_info[0]
            user_name = real_member_info[1]

            # Save to DB
            db.save_task_to_db(
                user_name, real_member_id, group_name['group_name'], 
                'Assigned', 'Tester', 'no deadline', current_date
            )

            

            # **Show remaining members after assigning Tester**
            selected_member_ids = {member['member_id'] for member in selected_members[user_id]}
            remaining_members = [
                {'member_id': str(m[0]), 'name': m[1]} if isinstance(m, tuple) else m
                for m in all_members
                if str(m[0] if isinstance(m, tuple) else m['member_id']) not in selected_member_ids
            ]

            if remaining_members:
                markup = create_member_for_role(remaining_members)
                await message.answer("Select a member for the role", reply_markup=markup)
                await NewTaskStates.waiting_for_member.set()
            else:
                await message.answer("All members have been assigned.")
                await state.finish()

            return

    # Continue if not a Tester role
    await state.update_data(role=role)
    await message.answer("Please provide a brief description of the work to be done.")
    await NewTaskStates.waiting_for_task_summary.set()


async def process_task_summary(message: types.Message, state: FSMContext):
    await state.update_data(task_summary=message.text)
    await message.answer("Enter a deadline in days (e.g., 3):")
    await NewTaskStates.waiting_for_deadline.set()


async def process_deadline(message: types.Message, state: FSMContext):
    deadline = int(message.text)
    user_data = await state.get_data()
    user_id = message.from_user.id

    # Initialize selected_members if not exists
    if user_id not in selected_members:
        selected_members[user_id] = []

    # Retrieve the last assigned member
    if isinstance(user_data['selected_members'][-1], str):  
        member_id = user_data['selected_members'].pop()
    else:
        member_id = user_data['selected_members'][-1]['member_id']

    # Create task data
    task_data = {
        "member_id": member_id,
        "role": user_data['role'],
        "task_summary": user_data['task_summary'],
        "deadline": deadline
    }
    selected_members[user_id].append(task_data)

    # Retrieve group and members
    group_name = db.get_group_name_by_id(user_id)
    all_members = db.get_members(group_name['group_name'])

    # Remove assigned members from selection list
    assigned_member_ids = {member['member_id'] for member in selected_members[user_id] if isinstance(member, dict)}
    remaining_members = [m for m in all_members if (m[0] if isinstance(m, tuple) else m['member_id']) not in assigned_member_ids]

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    if remaining_members:
        print("Sended")
        await show_member_selection(message, remaining_members, state)

        real_member_info = next((m for m in all_members if m[0] == member_id), None)
        if real_member_info:
            real_member_id = real_member_info[0]
            user_name = real_member_info[1]

            # Notify user of new task
            await bot.send_message(chat_id=user_id, text=f"You have a new task:\n\n{task_data['task_summary']}\n\nDeadline: {task_data['deadline']} days")

            # Save task to DB
            db.save_task_to_db(
                user_name, real_member_id, group_name['group_name'], 
                'Assigned', task_data["task_summary"], task_data['deadline'],
                current_date
            )

            await NewTaskStates.waiting_for_member.set()

    else:
        await message.answer("All members have been assigned.")

        real_member_info = next((m for m in all_members if m[0] == member_id), None)
        if real_member_info:
            real_member_id = real_member_info[0]
            user_name = real_member_info[1]

            # Update selected members for final database save
            selected_members[user_id] = [{'member_id': m['member_id']} for m in selected_members[user_id]]  
            unique_members = list({member['member_id'] for member in selected_members[user_id]})

            # Save created task to DB
            db.save_created_task_to_db(task_data_full['task_name'], task_data_full['task_description'], unique_members[0], 'In Process', group_name['group_name'])
            
            await bot.send_message(chat_id=user_id, text=f"You have a new task:\n\n{task_data['task_summary']}\n\nDeadline: {task_data['deadline']} days")
            
            db.save_task_to_db(
                user_name, real_member_id, group_name['group_name'], 
                'Assigned', task_data["task_summary"], task_data['deadline'],
                current_date
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
    dp.register_callback_query_handler(member_selected, lambda c: c.data.startswith("role_"), state=NewTaskStates.waiting_for_member)
    dp.register_callback_query_handler(done_assigning, lambda c: c.data == "done_selection", state=NewTaskStates.waiting_for_member)
