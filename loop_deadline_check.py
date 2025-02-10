from datetime import datetime, timedelta
from sqlcommands import TaskManagerDB
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '7079476232:AAFiUAqn3FAVXp4P-m_Uelt4241DtDgOZp8'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

db = TaskManagerDB()

def check_deadline(registered_date_str, deadline_days):
    # Convert the registered date string to a datetime object
    registered_date = datetime.strptime(registered_date_str, '%Y-%m-%d %H:%M')
    
    # Calculate the deadline date
    deadline_date = registered_date + timedelta(days=int(deadline_days))
    
    # Get the current date and time
    current_date = datetime.now()
    
    # Calculate the remaining time
    remaining_time = deadline_date - current_date
    remaining_days = remaining_time.days
    remaining_hours, remainder = divmod(remaining_time.seconds, 3600)
    remaining_minutes = remainder // 60
    
    return remaining_days, remaining_hours, remaining_minutes

def main():
    data = db.fetch_deadline()
    return data

async def send_deadline_message():
    while True:
        data = main()
        if not data:
            print("Waiting for data")
        else:
            for record in data:
                # Assuming record[1] is the registered date and record[2] is the user ID
                deadline_days = record[0]
                registered_date_str = record[1]
                user_id = record[2]

                # **Skip if deadline is "no deadline"**
                if deadline_days == "no deadline":
                    continue  

                # Convert deadline_days to integer
                try:
                    deadline_days = int(deadline_days)
                except ValueError:
                    continue  # Skip if conversion fails

                remaining_days, remaining_hours, remaining_minutes = check_deadline(registered_date_str, deadline_days)

                if remaining_days >= 0:
                    message = (f"Remaining time: {remaining_days} days, {remaining_hours} hours, {remaining_minutes} minutes")
                    await bot.send_message(chat_id=user_id, text=message)

                # Check if remaining time is 0 or negative and delete from workers table
                if remaining_days <= 0:
                    db.delete_from_workers(user_id)
                    msg = (f"You failed to complete this task on time, you will receive -5 points.")
                    await bot.send_message(chat_id=user_id, text=msg)

        # Sleep for 24 hours (86400 seconds)
        await asyncio.sleep(86400)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_deadline_message())
    executor.start_polling(dp, skip_updates=True)