import mysql.connector
from db_management.database import cursor, db


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
