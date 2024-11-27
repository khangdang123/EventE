import sqlite3

def get_database_connection():
    connection = sqlite3.connect("event_management.db")
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def insert_event(event_id, event_name, event_date):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO EVENT (EVENT_ID, EVENT_NAME, EVENT_DATE) VALUES (?, ?, ?);",
                (event_id, event_name, event_date),
            )
            connection.commit()
            print("Event added successfully.")
        except sqlite3.Error as e:
            print(f"Error inserting event: {e}")
        finally:
            connection.close()