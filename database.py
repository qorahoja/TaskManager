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
                task_deadline TEXT NOT NULL,
                task_participants TEXT NOT NULL,  -- Comma-separated list of user IDs
                task_status TEXT DEFAULT 'pending'  -- e.g., pending, completed
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

        # Commit the changes and close the cursor
        self.conn.commit()

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    db = TaskManagerDB()
    db.close()
