import mysql.connector
from db_management.database import cursor, db
import hashlib
import os
PEPPER = "SECRET_KEY"

def create_secure_password(password):
    salt = os.urandom(16)
    iterations = 100_000
    hash_value = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8') + PEPPER.encode('utf-8'),
        salt,
        iterations
    )
    password_hash = salt + hash_value
    return password_hash


def create_user(username, password):
    password_hash = create_secure_password(password)
    salt, key = password_hash[:16], password_hash[16:]
    hash_algo = "PBKDF2"
    iterations = 100_000


    insert_sql = (
        "INSERT INTO account (username, password_hash, salt, "
        "hash_algo, iterations) "
        "VALUES (%s, %s, %s, %s, %s)"
    )

    try:
        cursor.execute(insert_sql, (
            username,
            key,
            salt,
            hash_algo,
            iterations
        ))
        db.commit()
        print(f"User '{username}' created successfully.")
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # MySQL error code for duplicate entry
            print(f"Error: Username '{username}' already exists.")
        else:
            print(f"Error: {e}")

def verify_password(stored_password: bytes, provided_password: str, salt: bytes, iterations: int) -> bool:
    hash_value = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8') + PEPPER.encode('utf-8'),
        salt,
        iterations
    )
    return hash_value == stored_password

def verify_account(username, password):
    select_sql = "SELECT username, password_hash, salt, hash_algo, iterations FROM account WHERE username = %s"
    cursor.execute(select_sql, (username,))
    account = cursor.fetchone()

    if not account:
        print("Invalid username")
        return False

    stored_password_hash, salt, hash_algo, iterations = account[1], account[2], account[3], account[4]

    if verify_password(stored_password_hash, password, salt, iterations):
        print("Login successful")
        return True
    else:
        print("Invalid password")
        return False