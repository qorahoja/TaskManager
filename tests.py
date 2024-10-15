import base64
from cryptography.fernet import Fernet

class Encryptor:
    def __init__(self, key):
        self.cipher_suite = Fernet(key)

    def generate_encrypted_string(self, group_name):
        # Create an encrypted string using group_name
        encrypted_bytes = self.cipher_suite.encrypt(group_name.encode())
        # Encode to URL-safe Base64
        encoded_string = base64.urlsafe_b64encode(encrypted_bytes).decode()
        
        # Remove padding and custom shorten
        shortened_string = self.custom_shorten(encoded_string)
        
        return shortened_string, encoded_string  # Returning as a tuple

    def decrypt_string(self, shortened_string):
        # Reverse the custom shortening
        original_encoded_string = self.reverse_custom_shorten(shortened_string)
        print(original_encoded_string)
        # Decode from URL-safe Base64
        encrypted_bytes = base64.urlsafe_b64decode(original_encoded_string)
        print(encrypted_bytes)
        # Decrypt the encrypted bytes
        decrypted_string = self.cipher_suite.decrypt(encrypted_bytes).decode()
        print(decrypted_string)
        return decrypted_string

    def custom_shorten(self, encoded_string):
        # Implement your custom shortening logic here
        return encoded_string[:20]  # Example: Shorten to the first 20 characters

    def reverse_custom_shorten(self, shortened_string):
        # Implement the logic to recover the original encoded string
        # This is a placeholder; you need to implement your logic here.
        return shortened_string + "..."  # Placeholder logic

# Example usage
key = Fernet.generate_key()  # Generate a key for demonstration
encryptor = Encryptor(key)

# Generate an encrypted string
shortened, original = encryptor.generate_encrypted_string("MyGroupName")
print(f"Shortened: {shortened}")

print(original)
# Decrypt    the group name
decrypted_string = encryptor.decrypt_string(original)
print(f"Decrypted: {decrypted_string}")
