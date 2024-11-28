import sqlite3
import os
from feature import insert_event, delete

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

if __name__ == "__main__":
    main()

    insert_event()
    # delete()

