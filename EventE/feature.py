import sqlite3

def get_database_connection():
    connection = sqlite3.connect("event_management.db")
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def insert_event():
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
            
            # Extract non-primary key columns
            non_primary_columns = [col for col in columns_info if col[5] != 1]
            columns = [col[1] for col in non_primary_columns]
            print(f"Columns available for insertion in {table_name}: {', '.join(columns)}")

            # Determine if any column is a foreign key
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            foreign_key_mapping = {fk[3]: fk[2] for fk in foreign_keys}  # Maps column name to referenced table

            values = []
            for column in columns:
                if column in foreign_key_mapping:
                    referenced_table = foreign_key_mapping[column]
                    print(f"{column} is a foreign key referencing {referenced_table}.")
                    # Fetch existing keys in the referenced table for the user to choose from
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