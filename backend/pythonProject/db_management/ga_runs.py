import mysql.connector
from db_management.database import cursor, db

def insert_ga_run(filename, process_id, percent_complete, user_id):
    try:
        insert_query = """
        INSERT INTO ga_runs (filename, process_id, start_timestamp, stop_timestamp, percent_complete, user_id)
        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, %s)
        """
        cursor.execute(insert_query, (filename, process_id, percent_complete, user_id))
        db.commit()
        print("Insert successful")

    except mysql.connector.Error as err:
        print("Error: ", err)

def delete_ga_run(run_id):
    try:
        delete_query = "DELETE FROM ga_runs WHERE id = %s"
        cursor.execute(delete_query, (run_id,))
        db.commit()
        print("Delete successful")

    except mysql.connector.Error as err:
        print("Error: ", err)