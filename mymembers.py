from aiogram import types
from sqlcommands import TaskManagerDB
from imports import InlineButtons
db = TaskManagerDB()


async def handle_members(message: types.Message, admin_id: int):
    # Get the group name associated with the admin ID
    group_name = db.get_group_name_by_id(admin_id)

    if not group_name:
        await message.answer("Group not found.")
        return

    print(group_name['group_name'])
    members = db.get_members(group_name['group_name'])

    if not members:
        await message.answer("No members found in your group.")
        return

    # Create buttons for each member
    member_buttons = InlineButtons.create_members_button(members)
    await message.answer("Members of your group:", reply_markup=member_buttons)