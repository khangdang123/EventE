import sqlite3
import os
import math
from feature import insert, delete, retrieve,attendee_role,staff_role,register,measure_time

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

def main_menu():
    while True:
        print("ACCESS DATABASE")
        print("1. Attendee")
        print("2. Staff")
        print("3. Exit")

        role_choice = input("Enter Your Choice (1-3): ")

        if role_choice == "1":
            attendee_role()
        elif role_choice == "2":
            staff_role()
        elif role_choice == "3":
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")
            
if __name__ == "__main__":
    main()

    main_menu()

