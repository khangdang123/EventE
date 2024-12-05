import sqlite3
import os
import math
from feature import insert, delete, retrieve,attendee_role,staff_role,register,measure_time,get_database_connection

def insert_manual():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO Event (event_id, event_name, event_date)
        VALUES
            ('1', 'Charity Gala', '12/2/2024'),
            ('2', 'Health and Wellness Fair', '12/5/2024'),
            ('3', 'Starup Expo', '12/8/2024'),
            ('4', 'Career Fair', '12/6/2024');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO Attendee (attendee_id, name, phone_number, event_id)
        VALUES
            ('1', 'Alex', '123456789', '1'),
            ('2', 'John', '135792468', '1'),
            ('3', 'Micheal', '123678459', '2'),
            ('4', 'Sarah', '132435467', '3'),
            ('5', 'David', '223344556', '4'),
            ('6', 'Brown', '102938465', '2'),
            ('7', 'Wilson', '233445567', '4'),
            ('8', 'Chris', '039478844', '3');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO STAFF (Staff_id, name, role, event_id)
        VALUES
            ('1', 'Alexender', 'Catering', '1'),
            ('2', 'Chris', 'Venue Manager', '2'),
            ('3', 'Hannah', 'Coordinator', '2'),
            ('4', 'Jenny', 'Technical', '3'),
            ('5', 'Topher', 'Choopper', '4'),
            ('6', 'Choppy', 'Manager', '3');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO SCHEDULE (schedule_id, start_date, end_date, event_id)
        VALUES
            ('1', '12/2/2024', '12/3/2024', '1'),
            ('2', '12/5/2024', '12/5/2024', '2'),
            ('3', '12/8/2024', '12/8/2024', '3'),
            ('4', '12/6/2024', '12/6/2024', '4');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO TASK (task_id, name, event_id)
        VALUES
            ('1', 'Collect Feedback', '1'),
            ('2', 'Book Venue', '2'),
            ('3', 'Document the Event', '3'),
            ('4', 'Conduct Rehearsals', '4'),
            ('5', 'Secure Vendors', '2'),
            ('6', 'Plan Event', '1'),
            ('7', 'Design Invitations', '3');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO VENUE (venue_id, venue_name, location, capacity)
        VALUES
            ('1', 'Oceanview', 'New York', '100'),
            ('2', 'Starlight', 'New York', '200'),
            ('3', 'Maple', 'San Jose', '150'),
            ('4', 'Grand Horizon', 'San Francisco', '250');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO VENDOR (vendor_id, name, AVAILABILITY)
        VALUES
            ('1', 'Elite Catering', 'Yes'),
            ('2', 'Harmony Sound', 'Yes'),
            ('3', 'Bloom Floral', 'No'),
            ('4', 'Apex Supplies', 'Yes');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO SUPPLIES (supply_id, supply_name, quantity, vendor_id, event_id)
        VALUES
            ('1', 'Food and beverages', '10', '1', '1'),
            ('2', 'Plates', '20', '1', '1'),
            ('3', 'Speakers', '1', '2', '2'),
            ('4', 'LED screens', '2', '2', '1'),
            ('5', 'Bouquets', '1', '3', '2'),
            ('6', 'Floral Walls', '5', '3', '3'),
            ('7', 'Fans', '5', '4', '4'),
            ('8', 'Tents', '2', '4', '4');
        """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO WEATHER_CONDITION (dataset_id, temperature, wind_speed, event_id)
        VALUES
            ('1', '34.0', '12.6', '1'),
            ('2', '29.8', '19.9', '1'),
            ('3', '30.8', '12.1', '2'),
            ('4', '20.0', '11.7', '2'),
            ('5', '70.8', '12.2', '3'),
            ('6', '77.7', '20.2', '3'),
            ('7', '60.4', '24.1', '4'),
            ('8', '58.4', '22.7', '4');
        """)

    connection.commit()
    connection.close()

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
    insert_manual()
    main_menu()

