from aiogram import types

def create_group_buttons(groups):
    """Create inline keyboard buttons for the provided groups."""
    keyboard = types.InlineKeyboardMarkup()
    for group in groups:
        button = types.InlineKeyboardButton(
            text=group['group_name'],
            callback_data=f"join_group_{group['group_id']}"
        )
        keyboard.add(button)
    return keyboard
