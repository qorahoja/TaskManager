from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlcommands import TaskManagerDB
from InlineButtons import create_group_buttons  # Import the function to create buttons

async def show_my_groups(message: types.Message):
    user_id = message.from_user.id  # Get the Telegram user ID
    db = TaskManagerDB()
    
    # Retrieve groups associated with the user_id
    groups = db.get_user_groups(user_id)  # You need to implement this method in sqlcommands.py

    if not groups:
        await message.reply("You have no groups.")
        return

    # Create inline keyboard with group names using the function from InlineButtons.py
    keyboard = create_group_buttons(groups)

    await message.reply("Here are your groups:", reply_markup=keyboard)
    db.close()
