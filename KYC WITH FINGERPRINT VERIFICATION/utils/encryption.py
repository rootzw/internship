from cryptography.fernet import Fernet
import base64
import os

# Generate a key for encryption
def generate_key():
    return base64.urlsafe_b64encode(os.urandom(32))

# Encrypt data
def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data)

# Decrypt data
def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)