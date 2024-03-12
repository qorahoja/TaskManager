import sqlite3

# Connect to the database (create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_name TEXT NOT NULL,
        user_pass TEXT NOT NULL
    )
''')

# Create Groups table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY,
        group_name TEXT,
<<<<<<< HEAD
        group_admin INTEGER
=======
        group_admin TEXT
>>>>>>> 5b93596891c0da279334069535f49c9eb2e22931
    )
''')

# Create Members table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        member_id INTEGER PRIMARY KEY,
        member_name TEXT,
        group_name TEXT,
        member_status TEXT
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
