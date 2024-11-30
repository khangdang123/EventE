import sqlite3
import os
from feature import insert_event, delete, retrieve_data

def create_database_from_schema (db_name, schema_file):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    with open(schema_file, 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    conn.commit()
    conn.close()

def main():
    db_name = 'event_management.db'
    schema_file = 'schema.sql'

    create_database_from_schema(db_name, schema_file)

def attendee_role():
    while True:
        print("Welcome Attendee")
        print("1. Register Event")
        print("2. View Event Schedule")
        print("3. View weather conditions")
        print("4. Exit to main menu")
        choice = input("Enter your option: ")

def staff_role():
    while True:
        print("STAFF Information")
        print("1. Add/View events")
        print("2. Manage attendees")
        print("3. Manage schedules")
        print("4. View weather conditions")
        print("5. Exit to main")
        choice = input("Enter your option: ")
                
def main_menu():
    while True:
        print("ACCESS DATABASE")
        print("1. Attendee")
        print("2. Staff")
        print("3. Exit")

        role_choice = input("Enter Your Choice (1-3): ")

        if role_choice == "1":
            insert_event()
        elif role_choice == "2":
            delete()
        elif role_choice == "3":
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")
            
if __name__ == "__main__":
    main()


    #insert_event()
    # delete()
    # retrieve_data()

