from aiogram import types
from sqlcommands import TaskManagerDB

db = TaskManagerDB()  # Instantiate the database

async def handle_add_member(message: types.Message, admin_id):
    # Retrieve the group name from the database using the group_id
    group_info = db.get_group_name_by_id(admin_id)
    
    if group_info:
        group_name = group_info['group_name']  # Correctly access the group name from the dictionary
        unique_hash = db.generate_encrypted_string(group_name)  # Generate the unique hash
        invite_link = f"https://t.me/TaskTrackrBot?start={unique_hash[0]}"

        await message.answer(f"Invite link for adding a member: {invite_link}")
    else:
        await message.answer("Group not found.")
