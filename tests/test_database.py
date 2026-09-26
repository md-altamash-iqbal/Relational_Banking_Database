import sqlite3
import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.database import get_connection


def test_database_connection():
    connection = get_connection()

    try:
        assert connection is not None
        print("PASS: Database connection successful")
    finally:
        connection.close()


def test_foreign_keys_enabled():
    connection = get_connection()

    try:
        result = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

        assert result == 1
        print("PASS: Foreign keys are enabled")
    finally:
        connection.close()


def test_required_tables_exist():
    connection = get_connection()

    try:
        tables = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """).fetchall()

        table_names = {row[0] for row in tables}

        required_tables = {
            "branches",
            "customers",
            "accounts",
            "transactions"
        }

        assert required_tables.issubset(table_names)

        print("PASS: All required tables exist")
    finally:
        connection.close()


def test_row_counts():
    connection = get_connection()

    try:
        expected_counts = {
            "branches": 3,
            "customers": 6,
            "accounts": 10,
            "transactions": 10
        }

        for table, expected_count in expected_counts.items():
            actual_count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            assert actual_count == expected_count, (
                f"{table}: expected {expected_count}, "
                f"got {actual_count}"
            )

            print(
                f"PASS: {table} has {actual_count} rows"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    test_database_connection()
    test_foreign_keys_enabled()
    test_required_tables_exist()
    test_row_counts()

    print("\nDATABASE TESTING COMPLETE")