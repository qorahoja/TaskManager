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
            callback_data=f"member_{member[1]}"  # Use member[0] for callback data
        )
        keyboard.add(button)
    return keyboard


def create_member_for_role(members):
    print("Creating inline buttons for members...")  # Debugging log
    keyboard = types.InlineKeyboardMarkup()
    
    for member in members:
        # Assuming member is a dictionary with keys 'member_id' and 'name'
        member_name = member.get('name', 'Unnamed Member')  # Use a default name if not present
        member_id = member['member_id']  # Access the member ID
        
        button = types.InlineKeyboardButton(
            text=member_id,
            callback_data=f"member_role_{member_id}"  # Use member ID for callback data
        )
        print(f"Adding button with callback_data: member_role_{member_id}")  # Log callback data
        keyboard.add(button)
    
    # Add a "Done" button to end member selection
    done_button = types.InlineKeyboardButton(text="Done", callback_data="done_selection")
    keyboard.add(done_button)

    return keyboard


def create_updated_keyboard(selected_member_id):
    keyboard = types.InlineKeyboardMarkup()
    # Example of how to add an updated button
    button_text = "✅ Selected"
    button = types.InlineKeyboardButton(
        text=button_text, 
        callback_data=f"member_role_{selected_member_id}"  # Still use the same callback data
    )
    keyboard.add(button)
    
    # Add a Done button at the end
    done_button = types.InlineKeyboardButton(
        text="Done", 
        callback_data="done_selection"
    )
    keyboard.add(done_button)

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

