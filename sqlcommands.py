import sqlite3

class TaskManagerDB:
    def __init__(self, db_name="taskmanager.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def register_user(self, user_id, user_name, user_pass):
        try:
            self.cursor.execute('''
                INSERT INTO users (user_id, user_name, user_pass)
                VALUES (?, ?, ?)
            ''', (user_id, user_name, user_pass))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # User already exists

    def get_user(self, user_id):
        self.cursor.execute('''
            SELECT * FROM users WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchone()
    
    def create_group(self, group_name, admin_id):
        self.cursor.execute('''
            INSERT INTO groups (group_name, admin_id) VALUES (?, ?)
        ''', (group_name, admin_id))
        self.conn.commit()

    def get_user_groups(self, user_id):
        """Retrieve groups where the user is the admin."""
        self.cursor.execute('''
            SELECT group_id, group_name
            FROM groups
            WHERE admin_id = ?
        ''', (user_id,))
        
        return [{'group_id': row[0], 'group_name': row[1]} for row in self.cursor.fetchall()]




    def close(self):
        self.conn.close()
