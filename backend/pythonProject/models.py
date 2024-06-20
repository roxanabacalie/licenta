import mysql.connector
import os
import hashlib

PEPPER = "SECRET_KEY"

db = mysql.connector.connect(
    host="localhost",
    user="roxana",
    password="pass",
    database="licenta"
)
cursor = db.cursor()

def insert_route(start_id, stop_id, medium_time, night_time, distance, actual_time, demand):
    insert_sql = (
        "INSERT INTO route (start_id, stop_id, medium_time, night_time, distance, actual_time, demand) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    try:
        cursor.execute(insert_sql, (
            start_id,
            stop_id,
            medium_time,
            night_time,
            distance,
            actual_time,
            demand
        ))
        db.commit()
        print(f"Route '{start_id}'-'{stop_id}' created successfully.")
    except mysql.connector.IntegrityError as e:
            print(f"Error: {e}")

def get_route_time(start_id, stop_id):
    select_sql = (
        "SELECT actual_time "
        "FROM route "
        "WHERE start_id = %s AND stop_id = %s"
    )
    try:
        cursor.execute(select_sql, (start_id, stop_id))
        route = cursor.fetchone()  # Assuming we expect only one result
        if route:
            return route[0]
        else:
            print(f"No route found with start_id={start_id} and stop_id={stop_id}")
            return None
    except mysql.connector.Error as e:
        print(f"Error fetching route: {e}")
        return None

def get_route_demand(start_id, stop_id):
    select_sql = (
        "SELECT demand "
        "FROM route "
        "WHERE start_id = %s AND stop_id = %s"
    )
    try:
        cursor.execute(select_sql, (start_id, stop_id))
        route = cursor.fetchone()  # Assuming we expect only one result
        if route:
            return route[0]
        else:
            print(f"No route found with start_id={start_id} and stop_id={stop_id}")
            return None
    except mysql.connector.Error as e:
        print(f"Error fetching route: {e}")
        return None

def get_route_medium_time(start_id, stop_id):
    select_sql = (
        "SELECT medium_time "
        "FROM route "
        "WHERE start_id = %s AND stop_id = %s"
    )
    try:
        cursor.execute(select_sql, (start_id, stop_id))
        route = cursor.fetchone()  # Assuming we expect only one result
        if route:
            return route[0]
        else:
            print(f"No route found with start_id={start_id} and stop_id={stop_id}")
            return None
    except mysql.connector.Error as e:
        print(f"Error fetching route: {e}")
        return None

def update_medium_time(start_id, stop_id, medium_time):
    update_sql = (
        "UPDATE route "
        "SET medium_time = %s "
        "WHERE start_id = %s AND stop_id = %s"
    )
    try:
        cursor.execute(update_sql, (medium_time, start_id, stop_id))
        db.commit()
        print(f"Medium time updated successfully for route '{start_id}'-'{stop_id}'.")
    except mysql.connector.Error as e:
        print(f"Error updating medium time: {e}")

def update_actual_time(start_id, stop_id, actual_time):
    update_sql = (
        "UPDATE route "
        "SET actual_time = %s "
        "WHERE start_id = %s AND stop_id = %s"
    )
    try:
        cursor.execute(update_sql, (actual_time, start_id, stop_id))
        db.commit()
        print(f"Medium time updated successfully for route '{start_id}'-'{stop_id}'.")
    except mysql.connector.Error as e:
        print(f"Error updating medium time: {e}")

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

create_user('testuser', 'my_secure_password')
create_user('test', 'test')
verify_account('testuser', 'my_secure_password')

