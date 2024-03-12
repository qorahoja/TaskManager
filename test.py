import uuid
import random
import string

def generate_token(group_name):
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"https://t.me/TaskTrackrBot?start={group_name}_{random_part}"

# Example usage:
group_name = "YourGroupName"
token = generate_token(group_name)
print(token)  # Example output: YourGroupName_AbCdEf123456
