from aiogram import types
from KeyboardButtons import create_group_action_buttons  # Import the function for action buttons
from bot import bot  # Import the bot instance here to avoid circular imports

async def handle_group_selection(callback_query: types.CallbackQuery, chat_id, message_id):
    group_id = int(callback_query.data.split("_")[2])  # Extract the group ID
    group_name = f"Group ID: {group_id}"  # Placeholder for group name retrieval

    # Delete the previous message using chat_id and message_id
    await bot.delete_message(chat_id, message_id)

    # Send a message to the user and display action buttons
    await bot.send_message(
        callback_query.from_user.id,
        f"You are now in the {group_name}. What would you like to do?",
        reply_markup=create_group_action_buttons()  # Display action buttons
    )
