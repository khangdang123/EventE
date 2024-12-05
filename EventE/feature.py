import sqlite3
import time 
from datetime import datetime

def measure_time(func):
    def wrapper (*args, **kwargs):
        start_time = time.time()
        result = func(*ags, **kwargs)
        end_time = time.time()
        print(f"Execution time of {func.__name__}: {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def get_database_connection():
    connection = sqlite3.connect("event_management.db")
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def insert():
    connection = get_database_connection()

    if connection:
        try:
            table_name = input("Enter the table name (e.g., EVENT, ATTENDEE, STAFF): ").upper()

            cursor = connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            if not columns_info:
                print(f"Table '{table_name}' does not exist.")
                return
            
            non_primary_columns = [col for col in columns_info if col[5] != 1]
            columns = [col[1] for col in non_primary_columns]
            print(f"Columns available for insertion in {table_name}: {', '.join(columns)}")

            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            foreign_key_mapping = {fk[3]: fk[2] for fk in foreign_keys}  

            values = []
            for column in columns:
                if column in foreign_key_mapping:
                    referenced_table = foreign_key_mapping[column]
                    print(f"{column} is a foreign key referencing {referenced_table}.")
                    cursor.execute(f"SELECT rowid, * FROM {referenced_table}")
                    rows = cursor.fetchall()
                    if rows:
                        print(f"Available options in {referenced_table}:")
                        for row in rows:
                            print(row)
                    value = input(f"Enter value for {column} (must match a valid key from {referenced_table}): ")
                else:
                    value = input(f"Enter value for {column} (or leave blank for NULL): ")

                values.append(value if value else None)

            placeholders = ", ".join("?" for _ in columns)
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            cursor.execute(sql, values)
            connection.commit()
            print(f"Row inserted successfully into {table_name}.")
        
        except sqlite3.Error as e:
            print(f"Error inserting row: {e}")
        
        finally:
            connection.close()

def delete():
    connection = get_database_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0].upper() for table in cursor.fetchall()]

        print("Available tables: " + ", ".join(tables))
        table_name = input("Enter the table name to delete from: ").upper()

        if table_name not in tables:
            print(f"Table '{table_name}' does not exist.")
            return

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1].upper() for col in cursor.fetchall()]
        print(f"Columns in {table_name}: {', '.join(columns)}")

        column_name = input("Enter the column name to identify the row: ").upper()
        if column_name not in columns:
            print(f"Column '{column_name}' does not exist in table '{table_name}'.")
            return

        row_id = input(f"Enter the value of {column_name} to delete: ").strip()

        cursor.execute(f"SELECT * FROM {table_name} WHERE {column_name} = ?", (row_id,))
        row = cursor.fetchone()

        if not row:
            print(f"No matching row found in table '{table_name}' with {column_name} = {row_id}.")
            return

        print(f"Row to be deleted: {row}")
        confirm = input(f"Are you sure you want to delete this row? (yes/no): ").lower()
        if confirm == "yes":
            cursor.execute(f"DELETE FROM {table_name} WHERE {column_name} = ?", (row_id,))
            connection.commit()
            print("Row deleted successfully.")
        else:
            print("Deletion canceled.")

    except sqlite3.Error as e:
        print(f"Error deleting row: {e}")

    finally:
        connection.close()

def retrieve():
    connection = get_database_connection()

    if connection:
        try:
            cursor = connection.cursor()

            cursor.execute("SELECT EVENT_ID, EVENT_NAME FROM EVENT")
            events = cursor.fetchall()

            if not events:
                print("No events found in the database.")
                return

            print("Available events:")
            for event_id, event_name in events:
                print(f"{event_id}: {event_name}")

            selected_event_name = input("Enter the event name to retrieve information for: ").strip()
            cursor.execute(
                "SELECT EVENT_ID FROM EVENT WHERE EVENT_NAME = ?",
                (selected_event_name,)
            )
            result = cursor.fetchone()

            if not result:
                print(f"No event found with the name '{selected_event_name}'.")
                return

            event_id_filter = result[0]

            print(f"Retrieving data for event '{selected_event_name}'.")

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]

            selected_tables = input(
                "Enter table names to query: "
            ).upper().split(',')

            if not selected_tables or selected_tables == ['']:
                selected_tables = table_names

            for table in selected_tables:
                table = table.strip()
                if table not in table_names:
                    print(f"Table '{table}' does not exist.")
                    continue

                cursor.execute(f"PRAGMA table_info({table})")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info]

                if "EVENT_ID" not in columns:
                    print(f"Table '{table}' does not have an EVENT_ID column; skipping.")
                    continue

                print(f"Columns in {table}: {', '.join(columns)}")
                selected_columns = input(
                    f"Enter column names to retrieve from {table} (comma-separated, or press Enter for all): "
                ).strip()

                if not selected_columns:
                    selected_columns = "*"
                else:
                    selected_columns = ", ".join(col.strip() for col in selected_columns.split(','))

                try:
                    sql = f"SELECT {selected_columns} FROM {table} WHERE EVENT_ID = ?"
                    cursor.execute(sql, (event_id_filter,))
                    rows = cursor.fetchall()

                    if rows:
                        print(f"Data from {table}:")
                        for row in rows:
                            print(row)
                    else:
                        print(f"No data found in {table} for event '{selected_event_name}'.")

                except sqlite3.Error as e:
                    print(f"Error retrieving data from {table}: {e}")

        except sqlite3.Error as e:
            print(f"Error retrieving data: {e}")

        finally:
            connection.close()

def register():
    connection = get_database_connection()
    if connection:
        try: 
            cursor = connection.cursor()

            cursor.execute("SELECT EVENT_NAME FROM EVENT")
            events = cursor.fetchall()
            if not events:
                print("No events available for registration.")
                return
                    
            print("Available Events:")
            print(f"{'Event Name':<20}")
            print("-" * 30)
            for event in events:
                print(f"{event[0]:<20}")

            event_name = input("Enter the Event you want to register for: ").strip()

            cursor.execute("SELECT EVENT_ID FROM EVENT WHERE EVENT_NAME = ?", (event_name,))
            event = cursor.fetchone()

            if not event:
                print(f"No event found with the name '{event_name}'. Please try again.")
                return
                    
            event_id = event[0]

            name = input("Enter your name: ")
            phone_number = input("Enter your phone number: ")

            cursor.execute(
                "INSERT INTO ATTENDEE (NAME, PHONE_NUMBER, EVENT_ID) VALUES (?,?,?)",
                (name, phone_number, event_id)
            )
            connection.commit()
            print(f"Registration successful! You have been added as an attendee for '{event_name}'.")
        except sqlite3.Error as e:
            print(f"Error registering for event: {e}")
        finally:
            connection.close()

def view_event_schedule():
    connection = get_database_connection()

    try:
        cursor = connection.cursor() 
        cursor.execute("""
            SELECT S.SCHEDULE_ID, E.EVENT_NAME, S.START_DATE, S.END_DATE
            FROM SCHEDULE S
            JOIN EVENT E ON S.EVENT_ID = E.EVENT_ID
            ORDER BY S.START_DATE;
        """)

        rows = cursor.fetchall()

        if rows:
            print(f"\n{'Schedule ID': <15} {'Event': <20} {'Start Date': <15} {'End Date': <15}")
            print("-" * 70)
            for row in rows:
                print(f"{row[0]:<15} {row[1]:<20} {row[2]:<15} {row[3]:<15}")
        else:
            print("No schedule data found.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

def view_attendees():
    connection = get_database_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT a.ATTENDEE_ID, a.NAME, a.PHONE_NUMBER, e.EVENT_NAME
            FROM ATTENDEE a
            JOIN EVENT e ON a.EVENT_ID = e.EVENT_ID
            """)
        attendees = cursor.fetchall()

        if not attendees:
            print("No attendees found.")
        else:
            print("Attendees:")
            print(f"{'ID':<10}{'Name':<20}{'Phone':<20}{'Event':<20}")
            print("-" * 70)
            for attendee in attendees:
                print(f"{attendee[0]:<10}{attendee[1]:<20}{attendee[2]:<20}{attendee[3]:<20}")
    except sqlite3.Error as e:
            print(f"Error retrieving attendees: {e}")
    finally:
        connection.close()
        
def attendee_role():
    while True:
        print("Welcome Attendee")
        print("1. Register Event")
        print("2. View Event Schedule")
        print("3. View weather conditions")
        print("4. Exit to main menu")
        choice = input("Enter your option: ")

        connection = get_database_connection()
        try:
            cursor = connection.cursor()

            if choice == "1":
                print("\nEnter your information....")
                register()
            if choice == "2":
                view_event_schedule()
            elif choice == "3":
                view_weather_condition()
            elif choice == '4':
                break
        finally:
            connection.close()


def view_weather_condition():
    connection = get_database_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT E.EVENT_NAME, E.EVENT_DATE, WC.TEMPERATURE, WC.WIND_SPEED
            FROM WEATHER_CONDITION WC
            JOIN EVENT E ON WC.EVENT_ID = E.EVENT_ID
            ORDER BY E.EVENT_NAME;
        """)

        rows = cursor.fetchall()

        if rows:
            # Increase the width for event name
            print(f"\n{'Event Name': <40} {'Event Day': <15} {'Weather Condition': <20} {'Temperature': <20} {'Wind Speed (km/h)': <20}")
            print("-" * 120)  # Adjust separator length

            for row in rows:
                event_name, event_date, temperature, wind_speed = row

                # Adjust date format based on what is returned (MM/DD/YYYY format)
                try:
                    event_day = datetime.strptime(event_date, '%m/%d/%Y').strftime('%A')  # Correct date format
                except ValueError:
                    event_day = "Invalid Date"

                # Print the event information with increased space for the name
                print(f"{event_name:<40} {event_day:<15} {temperature:<20} {wind_speed:<20}")
        else:
            print("No weather conditions data found.")

    except sqlite3.Error as e:
        print(f"An error occurred while fetching weather conditions: {e}")
    finally:
        connection.close()


def get_supplies_for_events():
    connection = get_database_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT E.EVENT_NAME, 
                   V.NAME AS VENDOR_NAME, 
                   S.SUPPLY_NAME, 
                   S.QUANTITY
            FROM EVENT E
            JOIN SUPPLIES S ON E.EVENT_ID = S.EVENT_ID
            JOIN VENDOR V ON S.VENDOR_ID = V.VENDOR_ID
            ORDER BY E.EVENT_NAME, V.NAME;
        """)

        supplies_data = cursor.fetchall()

        for supply in supplies_data:
            print(f"Event: {supply[0]}, Vendor: {supply[1]}, Supply: {supply[2]}, Quantity: {supply[3]}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

def view_event_info(event_id):
    # Connect to the database
    connection = sqlite3.connect('event_management.db')
    cursor = connection.cursor()
    
    # Retrieve event information, including attendees, weather, staff roles, vendors, and supplies
    print(f"Event Information for Event ID: {event_id}\n")
    
    # Get event details
    cursor.execute("""
        SELECT EVENT_NAME, EVENT_DATE FROM EVENT WHERE EVENT_ID = ?
    """, (event_id,))
    event_info = cursor.fetchone()
    if event_info:
        print(f"Event Name: {event_info[0]}")
        print(f"Event Date: {event_info[1]}")
    else:
        print("Event not found.\n")
        connection.close()
        return
    
    # Get attendees for the event
    print("\nAttendees:")
    cursor.execute("""
        SELECT NAME, PHONE_NUMBER FROM ATTENDEE WHERE EVENT_ID = ?
    """, (event_id,))
    attendees = cursor.fetchall()
    if attendees:
        for attendee in attendees:
            print(f"Name: {attendee[0]}, Phone: {attendee[1]}")
    else:
        print("No attendees found.")
    
    # Get weather conditions for the event
    print("\nWeather Conditions:")
    cursor.execute("""
        SELECT TEMPERATURE, WIND_SPEED FROM WEATHER_CONDITION WHERE EVENT_ID = ?
    """, (event_id,))
    weather = cursor.fetchall()
    if weather:
        for record in weather:
            print(f"Temperature: {record[0]}°C, Wind Speed: {record[1]} km/h")
    else:
        print("No weather data found.")
    
    # Get staff and their roles for the event
    print("\nStaff and Roles:")
    cursor.execute("""
        SELECT NAME, ROLE FROM STAFF WHERE EVENT_ID = ?
    """, (event_id,))
    staff = cursor.fetchall()
    if staff:
        for member in staff:
            print(f"Name: {member[0]}, Role: {member[1]}")
    else:
        print("No staff found.")
    
    # Get vendors and their supplies for the event
    print("\nVendors and Supplies:")
    cursor.execute("""
        SELECT VENDOR.NAME, SUPPLIES.SUPPLY_NAME, SUPPLIES.QUANTITY
        FROM VENDOR
        JOIN SUPPLIES ON VENDOR.VENDOR_ID = SUPPLIES.VENDOR_ID
        WHERE SUPPLIES.EVENT_ID = ?
    """, (event_id,))
    vendor_supplies = cursor.fetchall()
    if vendor_supplies:
        for vendor in vendor_supplies:
            print(f"Vendor: {vendor[0]}, Supply: {vendor[1]}, Quantity: {vendor[2]}")
    else:
        print("No vendors or supplies found.")
    
    # Close the database connection
    connection.close()

def cancel_event():
    connection = get_database_connection()

    try:
        cursor = connection.cursor()

        # Fetch all events
        cursor.execute("SELECT EVENT_ID, EVENT_NAME FROM EVENT")
        events = cursor.fetchall()

        if not events:
            print("No events found to cancel.")
            return

        print("Available events:")
        for event_id, event_name in events:
            print(f"{event_id}: {event_name}")

        # Ask staff for the event name to cancel
        event_name_to_cancel = input("Enter the name of the event to cancel: ").strip()

        cursor.execute("SELECT EVENT_ID FROM EVENT WHERE EVENT_NAME = ?", (event_name_to_cancel,))
        event = cursor.fetchone()

        if not event:
            print(f"No event found with the name '{event_name_to_cancel}'. Please try again.")
            return

        # Ask for confirmation before deleting the event
        confirm = input(f"Are you sure you want to cancel the event '{event_name_to_cancel}'? (yes/no): ").lower()
        if confirm == 'yes':
            event_id_to_cancel = event[0]

            # Deleting the event from the EVENT table
            cursor.execute("DELETE FROM EVENT WHERE EVENT_ID = ?", (event_id_to_cancel,))
            connection.commit()
            print(f"The event '{event_name_to_cancel}' has been canceled successfully.")

        else:
            print("Event cancellation canceled.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        connection.close()

def staff_role():
    while True:
        print("STAFF Information")
        print("1. Insert/Delete information")
        print("2. Manage attendees")
        print("3. View weather conditions")
        print("4. View data based on Event Selected")
        print("5. View Event Schedule")
        print("6. Staff and Their Roles for Each Event")
        print("7. Find Events That Have Vendors and Their Supplies")
        print("8. View event information")
        print("9. Cancel Event")  # New option to cancel event
        print("10. Exit to main")
        choice = input("Enter your option: ")

        connection = get_database_connection()
        try:
            cursor = connection.cursor()

            if choice == "1":
                print("Modify Database")
                print("1. Insert information")
                print("2. Delete row information")
                print("3. Exit to main")
                choice1 = input("Enter your option: ")

                if choice1 == "1":
                    insert()
                if choice1 == "2":
                    delete()
                if choice1 == "3":
                    break

            if choice == "2":
                print("1. View Attendees")
                print("2. Access Attendees Role")
                print("3. Exit")
                choice = input("Enter your option: ")

                if choice == "1":
                    view_attendees()
                if choice == "2":
                    attendee_role()
                if choice == "3":
                    break
            if choice == "3":
                view_weather_condition()
            if choice == "4":
                retrieve()
            if choice == "5":
                view_event_schedule()
            if choice == "6":
                get_staff_for_events()
            if choice == "7":
                get_supplies_for_events()
            if choice == "8":
                event_id = input("Enter Event ID to view information: ")
                view_event_info(event_id)
            if choice == "9":  
                cancel_event()
            elif choice == "10":
                break
        finally:
            connection.close()
