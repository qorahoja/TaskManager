import sqlite3
import base64
import os
from cryptography.fernet import Fernet
import bcrypt

class TaskManagerDB:
    def __init__(self, db_name="taskmanager.db"):
        # Load or generate the Fernet key
        key_path = "secret.key"  # Define the path to store the key
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                self.key = key_file.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_path, 'wb') as key_file:
                key_file.write(self.key)
        
        self.cipher_suite = Fernet(self.key)  # Create cipher suite with key
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

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
    

    def get_group_name_by_id(self, admin_id):
        self.cursor.execute('''
            SELECT group_name FROM groups WHERE admin_id = ?
        ''', (admin_id,))
        result = self.cursor.fetchone()
        if result:
            return {'group_name': result[0]}  # Return dictionary with group_name key
        return None

    def update_username(self, user_id: int, new_username: str):
        self.cursor.execute('UPDATE users SET user_name = ? WHERE user_id = ?', (new_username, user_id))
        self.conn.commit()

    def update_password(self, user_id: int, new_password: str):
        self.cursor.execute('UPDATE users SET user_pass = ? WHERE user_id = ?', (new_password, user_id))
        self.conn.commit()

    def check_user_exists(self, user_id: int):
        self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()  # Fetch one record that matches the user_id
        return result  # This will return None if the user does not exist

    def is_admin(self, user_id: int):
        self.cursor.execute("SELECT admin_id FROM groups WHERE admin_id = ?", (user_id,))
        result = self.cursor.fetchone()  # Fetch one record that matches the admin_id
        return result is not None  # Return True if the user is an admin, otherwise False


    def add_member_to_group(self, user_id: int, user_name: str, group_name: str):
        self.cursor.execute('''
            INSERT INTO members (user_id, user_name, group_name) VALUES (?, ?, ?)
        ''', (user_id, user_name, group_name))
        self.conn.commit()



    def get_members(self, group_name: str):
        self.cursor.execute('''
            SELECT user_name, user_id FROM members WHERE group_name = ?
        ''', (group_name,))
        result = self.cursor.fetchall()
        return result


    def delete_member(self, user_id: int):
        # SQL command to delete a member from the members table based on user ID
        self.cursor.execute('''
            DELETE FROM members WHERE user_id = ?
        ''', (user_id,))
        
        # Commit the changes to the database
        self.conn.commit()


    def history_of_user(self, group_name: str):
        self.cursor.execute("""
            SELECT task_participants, task_name, task_description, task_deadline 
            FROM tasks 
            WHERE group_name = ? AND task_status = 'Done'
        """, (group_name,))
        
        return self.cursor.fetchall()

    

    def get_user_completed_tasks(self, user_id: int):
        self.cursor.execute("""
            SELECT task_name, task_description, task_deadline, group_name 
            FROM tasks 
            WHERE task_status = 'Done' AND task_participants LIKE ?
        """, (f"%{user_id}%",))  # Using LIKE to match user ID in the participants
        
        return self.cursor.fetchall()


    def get_username_with_userid(self, user_id: int):
        self.cursor.execute("SELECT user_name FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        return result       

    # def get_user_id_by_userName(self, user_id: int):
    #     self.cursor.execute('''
    #         SELECT user_name FROM users WHERE user_id = ?
    #     ''', (user_id,))

    #     reslut = self.cursor.fetchone()

    #     return reslut

    def generate_encrypted_string(self, group_name):
        # Encrypt and encode the group_name
        encrypted_bytes = self.cipher_suite.encrypt(group_name.encode())
        encoded_string = base64.urlsafe_b64encode(encrypted_bytes).decode()
        
        # Shorten for the URL if necessary
        shortened_string = self.custom_shorten(encoded_string)

        # Debugging outputs
        print(f"Original Group Name: {group_name}")
        print(f"Generated Encoded String: {encoded_string}")
        print(f"Generated Shortened String: {shortened_string}")

        # Insert into database (both shortened and full encoded hash)
        self.cursor.execute('''
            INSERT INTO hash (shorted_hash, real_hash) VALUES (?, ?)
        ''', (shortened_string, encoded_string))
        self.conn.commit()

        return shortened_string, encoded_string

    def decrypt_string(self, encrypted_string: str):
        # Fetch the full real hash from the database
        self.cursor.execute('SELECT real_hash FROM hash WHERE shorted_hash = ?', (encrypted_string,))
        real_hash = self.cursor.fetchone()

        if not real_hash:
            print(f"No hash found for {encrypted_string}")
            return None

        # Debugging output
        print(f"Retrieved Real Hash from DB: {real_hash[0]}")

        try:
            # Decode from Base64
            encrypted_bytes = base64.urlsafe_b64decode(real_hash[0])
            print(f"Decoded Encrypted Bytes: {encrypted_bytes}")
        except Exception as e:
            print(f"Base64 Decoding Failed: {e}")
            return None

        try:
            # Decrypt the bytes
            decrypted_string = self.cipher_suite.decrypt(encrypted_bytes).decode()
            print(f"Decrypted String: {decrypted_string}")
            return decrypted_string
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    def custom_shorten(self, s):
        """Shortens a Base64 URL-safe string by removing padding and limiting to 20 chars."""
        return s.replace('=', '').replace('-', '').replace('_', '')[:20]

    def close(self):
        self.conn.close()

