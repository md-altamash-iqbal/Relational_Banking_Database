import sqlite3
import sys
from pathlib import Path

import pytest


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Add src directory to Python path
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

# Import actual production code
import database
import load_data


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """
    Create a fresh temporary database using the actual
    production database-building and data-loading code.
    """

    database_path = tmp_path / "test_banking.db"

    # Make database.py use the temporary database
    monkeypatch.setattr(database, "DATABASE_PATH", database_path)

    # Create database using actual production code
    database.create_database(database_path)

    # Load data using actual production code
    load_data.load_all_data(database_path)

    # Open the SAME temporary database
    connection = sqlite3.connect(database_path)

    # Enable foreign-key enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    yield connection

    connection.close()


def test_required_tables_exist(test_database):
    """Test that all required tables exist."""

    cursor = test_database.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
    """)

    tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        "branches",
        "customers",
        "accounts",
        "transactions",
    }

    assert expected_tables.issubset(tables)


def test_foreign_keys_are_enabled(test_database):
    """Test that SQLite foreign-key enforcement is enabled."""

    result = test_database.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    assert result == 1


def test_expected_row_counts(test_database):
    """Test that the expected number of records were loaded."""

    expected_counts = {
        "branches": 3,
        "customers": 6,
        "accounts": 10,
        "transactions": 10,
    }

    for table, expected_count in expected_counts.items():

        actual_count = test_database.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        assert actual_count == expected_count


def test_invalid_foreign_key_is_rejected(test_database):
    """Test that a transaction with a nonexistent account is rejected."""

    with pytest.raises(sqlite3.IntegrityError):

        test_database.execute("""
            INSERT INTO transactions (
                transaction_id,
                account_id,
                transaction_date,
                transaction_type,
                amount,
                currency
            )
            VALUES (
                'TEST_FK_001',
                'INVALID_ACCOUNT',
                '2026-09-25',
                'CREDIT',
                100.00,
                'INR'
            )
        """)

        test_database.commit()


def test_invalid_amount_is_rejected(test_database):
    """Test that a negative transaction amount is rejected."""

    with pytest.raises(sqlite3.IntegrityError):

        test_database.execute("""
            INSERT INTO transactions (
                transaction_id,
                account_id,
                transaction_date,
                transaction_type,
                amount,
                currency
            )
            VALUES (
                'TEST_CHECK_001',
                'A1001',
                '2026-09-25',
                'CREDIT',
                -50.00,
                'INR'
            )
        """)

        test_database.commit()


def test_transaction_type_totals(test_database):
    """Test an important SQL analysis result from Part D."""

    rows = test_database.execute("""
        SELECT
            transaction_type,
            COUNT(*) AS transaction_count,
            ROUND(SUM(amount), 2) AS total_amount
        FROM transactions
        GROUP BY transaction_type
        ORDER BY transaction_type;
    """).fetchall()

    expected = [
        ("CREDIT", 5, 2975.00),
        ("DEBIT", 5, 450.50),
    ]

    assert rows == expected


def test_database_build_can_be_rerun_without_duplicates(
    test_database,
    monkeypatch
):
    """
    Test that the complete database rebuild and load process
    can be run again without creating duplicate records.
    """

    database_path = database.DATABASE_PATH

    # Rebuild the same temporary database
    database.create_database(database_path)

    # Reload the same temporary database
    load_data.load_all_data(database_path)

    expected_counts = {
        "branches": 3,
        "customers": 6,
        "accounts": 10,
        "transactions": 10,
    }

    for table, expected_count in expected_counts.items():

        actual_count = test_database.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        assert actual_count == expected_count