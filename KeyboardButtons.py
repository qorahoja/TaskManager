from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard():
    # Create buttons for registration and login
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    register_button = KeyboardButton("Register")
    login_button = KeyboardButton("Login")
    markup.add(register_button, login_button)
    return markup
def get_main_menu_keyboard():
    # Create buttons for the main menu
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    new_group_button = KeyboardButton("New Group")
    settings_button = KeyboardButton("Settings")
    my_groups_button = KeyboardButton("My Groups")
    markup.add(new_group_button, settings_button, my_groups_button)
    return markup



def create_group_action_buttons():
    """Create buttons for actions within a selected group."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Add Member")
    keyboard.add("Members")
    keyboard.add("Create Task")
    keyboard.add("History")
    return keyboard