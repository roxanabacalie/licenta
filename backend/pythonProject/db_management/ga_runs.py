import mysql.connector
from db_management.database import cursor, db

def insert_ga_run(filename, process_id, start_timestamp, stop_timestamp, percent_complete, user_id):
    try:
        insert_query = """
        INSERT INTO ga_runs (filename, process_id, start_timestamp, stop_timestamp, percent_complete, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (filename, process_id, start_timestamp, stop_timestamp, percent_complete, user_id))
        db.commit()
        print("Insert successful")
        return cursor.lastrowid

    except mysql.connector.Error as err:
        print("Error: ", err)
        return None

def delete_ga_run(run_id):
    try:
        delete_query = "DELETE FROM ga_runs WHERE id = %s"
        cursor.execute(delete_query, (run_id,))
        db.commit()
        print("Delete successful")

    except mysql.connector.Error as err:
        print("Error: ", err)


def update_stop_timestamp(run_id, stop_timestamp):
    try:
        update_query = "UPDATE ga_runs SET stop_timestamp = %s WHERE id = %s"
        cursor.execute(update_query, (stop_timestamp, run_id))
        db.commit()
        print("Stop timestamp updated successfully")

    except mysql.connector.Error as err:
        print("Error: ", err)


def update_percent_complete(run_id, percent_complete):
    try:
        update_query = "UPDATE ga_runs SET percent_complete = %s WHERE id = %s"
        cursor.execute(update_query, (percent_complete, run_id))
        db.commit()
        print("Percent complete updated successfully")

    except mysql.connector.Error as err:
        print("Error: ", err)

def update_filename(run_id, filename):
    try:
        update_query = "UPDATE ga_runs SET filename = %s WHERE id = %s"
        cursor.execute(update_query, (filename, run_id))
        db.commit()
        print("Filename updated successfully")

    except mysql.connector.Error as err:
        print("Error: ", err)

def get_last_filename():
    try:
        select_query = """
        SELECT filename 
        FROM ga_runs 
        WHERE filename IS NOT NULL 
        ORDER BY id DESC 
        LIMIT 1
        """
        cursor.execute(select_query)
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the filename
        else:
            print("No filename found")
            return None

    except mysql.connector.Error as err:
        print("Error: ", err)
        return None


def get_pid_by_userid(user_id):
    user_id = int(user_id)
    try:
        select_query = """
        SELECT process_id
        FROM ga_runs
        WHERE user_id = %s AND stop_timestamp IS NULL
        ORDER BY id DESC
        LIMIT 1
        """
        print(f"Executing query for user_id: {user_id}")
        cursor.execute(select_query, (user_id,))
        result = cursor.fetchone()

        if result:
            print(f"Found process_id {result[0]} for user_id {user_id}")
            return result[0]
        else:
            print(f"No running process found for user_id {user_id}")
            return None

    except mysql.connector.Error as err:
        print("Error: ", err)
        return None