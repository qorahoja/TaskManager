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


def create_members_button(members):
    keyboard = types.InlineKeyboardMarkup()
    for member in members:
        # Assume member[0] contains the user name; adjust if your structure is different
        button = types.InlineKeyboardButton(
            text=member[0], 
              # Accessing the username directly
            callback_data=f"info_{member[1]}"  # Use member[0] for callback data
        )
        keyboard.add(button)
    return keyboard


def create_member_action_buttons(user_id: int):
    keyboard = types.InlineKeyboardMarkup()

    buttons = [
        ('Remove user', f'remove_user_{user_id}'),
        # ('User achievements', f'user_achievements_{user_id}'),
        ('History', f'history_{user_id}'),
        ('Info', f'info_{user_id}')
    ]

    for button_text, callback_data in buttons:
        button = types.InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        )
        keyboard.add(button)

    return keyboard

