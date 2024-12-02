import sqlite3

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
        table_name = input("Enter the table name to delete from (e.g., EVENT, ATTENDEE, STAFF): ").upper()
        column_name = input(f"Enter the column name to identify the row (e.g., EVENT_ID, ATTENDEE_ID): ").upper()
        row_id = input(f"Enter the value of {column_name} to delete: ")

        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1].upper() for col in cursor.fetchall()]

        if column_name not in columns:
            print(f"Column '{column_name}' does not exist in table '{table_name}'.")
            return
        
        cursor.execute (f"SELECT * FROM {table_name} WHERE {column_name} = ?", (row_id,))
        row = cursor.fetchone()

        if row:
            confirm = input(f"Are you sure you want to delete this row from '{table_name}'? (yes/no): ")
            if confirm.lower() == "yes":
                cursor.execute(f"DELETE FROM {table_name} WHERE {column_name} = ?", (row_id,))
                connection.commit()
                print("Row deleted successfully.")
            else:
                print("Deletion canceled.")
        else:
            print(f"No matching row found in table '{table_name}' with {column_name} = {row_id}.")

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
                cursor.execute("""
                    SELECT S.SCHEDULE_ID, E.EVENT_NAME, S.START_DATE, S.END_DATE
                    FROM SCHEDULE S
                    JOIN EVENT E ON S.EVENT_ID = E.EVENT_ID
                    ORDER BY S.START_DATE;   
                """)
                rows = cursor.fetchall()
                if rows:
                    print(f"\n{'Schedule ID': <15} {'Event': 20} {'Start Date':<15} {'End Date':<15}")
                    print("-" * 70)
                    for row in rows:
                        print(f"{row[0]:<15} {row[1]:<20} {row[2]:<15} {row[3]:<15}")
                else:
                    print("No schedule data found.")
            elif choice == "3":
                print("\nRetrieving weather condition...")
                cursor.execute("SELECT * FROM WEATHER_CONDITION;")
                rows = cursor.fetchall()
                if rows:
                    print(f"\n{'Condition ID': <15} {row[1]:30}")
                    print("-" * 50)
                    for row in rows:
                        print(f"{rows[0]:<15} {row[1]:<30}")
                else:
                    print("No weather condition data found.")
            elif choice == '4':
                break
        finally:
            connection.close()

def staff_role():
    while True:
        print("STAFF Information")
        print("1. Insert/Delete Database")
        print("2. Manage attendees")
        print("3. View weather conditions")
        print("4. View data based on Event")
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
                choice = input("Enter your option: ")

                if choice == "1":
                    insert()
                if choice == "2":
                    delete()
                if choice == "3":
                    break
                else:
                    print("Invalid choice. Please try again.")
            if choice == "2":
                print("1. View Attendees")
                print("2. Access Attendees Role")
                print("3. Exit")
                choice = input("Enter your option: ")

                if choice == "1":
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
                if choice == "2":
                    attendee_role()
                if choice == "3":
                    break
            if choice == "3":
                print("\nRetrieving weather condition...")
                cursor.execute("SELECT * FROM WEATHER_CONDITION;")
                rows = cursor.fetchall()
                if rows:
                    print(f"\n{'Condition ID': <15} {row[1]:30}")
                    print("-" * 50)
                    for row in rows:
                        print(f"{rows[0]:<15} {row[1]:s<30}")
                else:
                    print("No weather condition data found.")
            if choice == "4":
                retrieve()
            elif choice == "10":
                break
        finally:
            connection.close()            
