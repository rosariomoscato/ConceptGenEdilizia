import sqlite3
import os

DATABASE_PATH = os.path.join(os.getcwd(), 'archive.db')

def initialize_database():
    """
    Initializes the database schema. Creates the 'requests' table if it doesn't exist.
    This script can be run manually to set up the database.
    """
    if os.path.exists(DATABASE_PATH):
        print(f"Database file already exists at {DATABASE_PATH}.")
    else:
        print(f"Database file does not exist. It will be created at {DATABASE_PATH}.")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if the table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='requests'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print("Creating 'requests' table...")
        cursor.execute('''
            CREATE TABLE requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT NOT NULL,
                flowise_response TEXT NOT NULL,
                gemini_image_url_1 TEXT NOT NULL,
                gemini_image_url_2 TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("'requests' table created successfully.")
    else:
        print("'requests' table already exists. No action taken.")

    conn.close()
    print("Database initialization process complete.")

if __name__ == '__main__':
    print("Initializing database...")
    initialize_database()
