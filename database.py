import sqlite3

# Connect to the database (create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_name TEXT,
        user_pass TEXT
    )
''')

# Create Groups table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY,
        group_name TEXT,
        group_admin INTEGER
    )
''')

# Create Members table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        member_id INTEGER PRIMARY KEY,
        member_name TEXT,
        rank_member TEXT,
        group_name TEXT,
        member_status TEXT,
        deadline TEXT
    )
''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS history(
               group_name TEXT,
               group_admin_id INTEGER,
               task_subject TEXT,
               started TEXT,
               finished TEXT               
            )


''')


cursor.execute('''
            CREATE TABLE IF NOT EXISTS workers_worked_tasks(
               worker_id INTEGER,
               group_name TEXT,
               point_for_this_task INTEGER,
               task_subject TEXT
            )


''')




# Create Admins table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY,
        admin_name TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database 'database.db' and tables created successfully.")
