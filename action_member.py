from aiogram import types
from sqlcommands import TaskManagerDB
from imports import InlineButtons, KeyboardButtons

db = TaskManagerDB()

async def handle_action(message: types.Message, user_id: int):
    markup = InlineButtons.create_member_action_buttons(user_id)
    await message.delete()
    await message.answer(f"Choose action for this user", reply_markup=markup)



async def handle_remove_user(message: types.Message, user_id: int):
    markup = KeyboardButtons.create_group_action_buttons()

    db.delete_member(user_id)

    await message.answer("User Kicked", reply_markup=markup)




async def handle_user_history(message: types.Message, admin_id: int, user_id: int):
    # Retrieve the group information based on admin ID
    group_info = db.get_group_name_by_id(admin_id)

    if group_info:
        group_name = group_info['group_name']

        # Fetch the user's name using user_id
        user_name = db.get_username_with_userid(user_id)[0].strip()  # Extracting and stripping the username

        # Fetch completed tasks for the group
        completed_tasks = db.history_of_user(group_name)

        print(f"User name: {user_name}")
        print(f"Participants: {completed_tasks}")

        # Prepare to collect the tasks related to the user
        user_tasks = []

        # Iterate through each task and check if the user is a participant
        for task in completed_tasks:
            # Each task is assumed to be a single string of participants
            task_participants = task[0].strip()  # Fetching the participants string

            # Split by comma to get individual user names
            participants_list = [p.strip() for p in task_participants.split(",")]

            print(f"Processed participants list: {participants_list}")

            # Check if the user's name exists in the participants list
            if user_name in participants_list:
                # If the user is a participant, collect the task information
                user_tasks.append(task)

        # If tasks are found, format them into a message
        if user_tasks:
            task_messages = []
            for task in user_tasks:
                task_name, task_description, task_deadline = task[1], task[2], task[3]
                task_messages.append(f"**Task Name:** {task_name}\n"
                                     f"**Description:** {task_description}\n"
                                     f"**Deadline:** {task_deadline}\n"
                                     f"**Group:** {group_name}\n")

            # Calculate total tasks for the user
            total_tasks = len(user_tasks)

            # Join all task messages into one string
            tasks_summary = "\n\n".join(task_messages)

            # Create the header with decoration
            header = f"🎉 **Completed Tasks for User:** '{user_name}' 🎉\n"
            header += f"**Total Completed Tasks:** {total_tasks}\n\n"
            header += "-----------------------------------\n\n"
            from imports import keyButton
            back = keyButton.create_back_button()
           
            
            # Send the summary of tasks back to the user
            await message.answer(f"{header}{tasks_summary}", parse_mode='Markdown', reply_markup=back)
            return True  # Indicate success
        else:
            print(f"No completed tasks found for user '{user_name}'.")
            await message.answer("No completed tasks found.")
            return False  # Indicate no tasks found
    else:
        print("No group found for the given admin_id.")
        await message.answer("Group not found.")
        return None  # Handle no group found



async def info_user(message: types.Message, user_id: int):
    
    # Fetch the user's information using user_id
    user_info = db.get_username_with_userid(user_id)
    print(user_info)
    # Check if the user exists in the database
    if user_info:
        user_name = user_info[0].strip()
        
        # Send a message with user information
        await message.answer(f"**User Information:**\n\n"
                                                               f"**Username:** {user_name}\n"
                                                               f"**User ID:** {user_id}",
                                                               parse_mode='Markdown')
    else:
        await message.answer("User not found.")

    # Always answer the callback to prevent the loading circle