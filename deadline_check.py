import schedule
import time
from datetime import datetime, timedelta
from sqlcommands import TaskManagerDB
import asyncio
db = TaskManagerDB()
def print_worker_statuses():
    try:
        # Fetch and organize worker data
        workers_data = db.fetch_data_from_workers()
        
        if not workers_data:
            print("No worker data found.")
            return
        
        sorted_workers = {}
        for worker in workers_data:
            user_id = worker['user_id']
            registered_data = worker.get('registred_data')
            if registered_data is None:
                print(f"User ID: {user_id} has no registered data. Skipping...")
                continue
            
            registered_date = datetime.strptime(registered_data, '%Y-%m-%d')
            deadline_days = int(worker['deadline'])
            days_since_registered = (datetime.now() - registered_date).days
            is_expired = days_since_registered > deadline_days
            
            sorted_workers[user_id] = {
                'user_name': worker['user_name'],
                'group_name': worker['group_name'],
                'status': worker['status'],
                'current_job': worker['current_job'],
                'deadline': worker['deadline'],
                'registred_data': registered_data,
                'days_since_registered': days_since_registered,
                'status_label': "expired" if is_expired else "on track"
            }
        
        sorted_workers = dict(sorted(sorted_workers.items(), key=lambda item: item[1]['days_since_registered']))
        for user_id, worker_info in sorted_workers.items():
            days_label = "days" if worker_info['days_since_registered'] != 1 else "day"
            print(f"User ID: {user_id}, Status: {worker_info['status_label']} ({worker_info['days_since_registered']} {days_label} since registered)")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# async def scheduler():
#     schedule.every(24).hours.do(print_worker_statuses)
#     while True:
#         schedule.run_pending()
#         await asyncio.sleep(60) 


print_worker_statuses()