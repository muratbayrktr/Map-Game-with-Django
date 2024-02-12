
import os
import sqlite3
import os
import sqlite3
from utils.singleton import Singleton

@Singleton
class Database:
    def __init__(self, db_file='database.db'):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.is_connected = False

    def connect(self):
        # Check if the database file exists
        if not os.path.exists(self.db_file):
            # Create a new database file
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.is_connected = True
            self.cursor = self.conn.cursor()

            # Read the schema.sql file
            with open('src/schema.sql', 'r') as file:
                schema = file.read()

            # Execute the schema.sql script to create the tables
            self.cursor.executescript(schema)

            # Commit the changes
            self.conn.commit()
        else:
            # Connect to the database
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.is_connected = True
            self.cursor = self.conn.cursor()

    def close(self):
        # Close the connection
        if self.conn:
            self.conn.commit()
            self.is_connected = False

    def execute(self, query, params=None):
        # Connect to the database if not connected
        if not self.conn:
            self.connect()

        # Execute the query
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        # Commit the changes
        self.conn.commit()

    def fetch_all(self, query, params=None):
        # Connect to the database if not connected
        if not self.conn:
            self.connect()

        # Execute the query and fetch all rows
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        r = self.cursor.fetchall()
        self.close()
        return r

    def fetch_one(self, query, params=None):
        # Connect to the database if not connected
        if not self.conn:
            self.connect()

        # Execute the query and fetch one row
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        r = self.cursor.fetchone()

        self.close()
        return r
