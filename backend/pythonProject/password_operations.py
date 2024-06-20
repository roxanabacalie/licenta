import hashlib
import os




def verify_password(stored_password: str, provided_password: str) -> bool:
    # Extract the salt from the stored password
    salt = stored_password[:16]
    # Extract the hashed password from the stored password
    stored_hash = stored_password[16:]
    # Hash the provided password with the extracted salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    # Compare the hashed password with the stored hash
    return pwdhash == stored_hash