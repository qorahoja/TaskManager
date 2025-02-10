import sqlite3

class TaskManagerDB:
    def __init__(self, db_name="taskmanager.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,  -- Telegram ID
                user_name TEXT NOT NULL,
                user_pass TEXT NOT NULL
            )
        ''')

        # Create tasks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                task_description TEXT,  -- Optional
                task_participants TEXT NOT NULL,  -- Comma-separated list of user IDs
                task_status TEXT DEFAULT 'pending',  -- Default value for task status
                group_name TEXT
                )
            ''')


        # Create groups table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for the group
                group_name TEXT NOT NULL UNIQUE,
                admin_id INTEGER
            )
        ''')


        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS hash (
                shorted_hash TEXT UNIQUE,
                real_hash TEXT
            )
        ''')


        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                user_id INT UNIQUE,
                user_name TEXT,
                group_name TEXT,
                joined_data TEXT,
                member_points INT DEFAULT 0,
                member_rank TEXT DEFAULT 'Bronze'
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS worker (
                user_id INT UNIQUE,
                user_name TEXT,
                group_name TEXT,  -- Renamed from "group"
                status TEXT,
                current_job TEXT,
                deadline INT,
                registred_data TEXT
            )
        ''')



        # Commit the changes and close the cursor
        self.conn.commit()

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    db = TaskManagerDB()
    db.close()
