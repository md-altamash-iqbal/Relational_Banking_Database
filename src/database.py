import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database and schema file paths
DATABASE_PATH = BASE_DIR / "banking.db"
SCHEMA_PATH = BASE_DIR / "src" / "schema.sql"


def get_connection(database_path=DATABASE_PATH):
    """
    Create and return a connection to the SQLite database.
    """

    connection = sqlite3.connect(database_path)

    # Enable foreign-key enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_database(database_path=DATABASE_PATH):
    """
    Create the database tables using schema.sql.
    """

    connection = get_connection(database_path)

    try:
        # Read the SQL schema
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        # Execute all SQL statements from schema.sql
        connection.executescript(schema)

        # Save the changes
        connection.commit()

        print("Database created successfully.")

    finally:
        connection.close()


def show_tables():
    """
    Display all tables in the database.
    """

    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
        """)

        tables = cursor.fetchall()

        print("\nTables in database:")

        for table in tables:
            print("-", table[0])

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
    show_tables()