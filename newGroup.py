from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlcommands import TaskManagerDB
from states import NewGroupStates

async def start_new_group(message: types.Message):
    await message.reply("Please enter the name of the new group:")
    await NewGroupStates.waiting_for_group_name.set()

async def process_new_group_name(message: types.Message, state: FSMContext):
    group_name = message.text
    user_id = message.from_user.id  # Get the user ID (admin)

    db = TaskManagerDB()

    try:
        # Attempt to create the new group in the database
        db.create_group(group_name, user_id)  # Ensure this method exists in sqlcommands.py
        await message.reply(f"Group '{group_name}' created successfully!")
    except Exception as e:
        await message.reply(f"Error creating group: {str(e)}")

    await state.finish()  # Clear state
    db.close()
