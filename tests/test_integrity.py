import sqlite3
import sys
from pathlib import Path


DB_PATH = "banking.db"
EVIDENCE_PATH = Path("evidence/integrity_tests.txt")


class Tee:
    """
    Sends printed output to both the terminal
    and the evidence text file.
    """

    def __init__(self, terminal, file):
        self.terminal = terminal
        self.file = file

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)

    def flush(self):
        self.terminal.flush()
        self.file.flush()


def run_test(test_name, expected_constraint, operation):

    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print(f"EXPECTED CONSTRAINT: {expected_constraint}")
    print("-" * 70)

    connection = sqlite3.connect(DB_PATH)

    # Enable foreign-key enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        operation(connection)

        # If we reach here, the invalid operation was NOT rejected.
        print("RESULT: FAIL")
        print("ERROR: Invalid data was accepted.")

        # Never allow an invalid test operation to remain in the database.
        connection.rollback()

    except sqlite3.IntegrityError as error:
        print(f"SQLITE ERROR: {error}")
        print("RESULT: PASS")

        # Make sure the deliberately invalid operation is not persisted.
        connection.rollback()

    finally:
        connection.close()


# ============================================================
# TEST 1
# Transaction references nonexistent account
# ============================================================

def test_nonexistent_account(connection):

    connection.execute("""
        INSERT INTO transactions (
            transaction_id,
            account_id,
            transaction_date,
            transaction_type,
            amount,
            currency,
            source_file
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEST-TXN-001",
        "NONEXISTENT-ACCOUNT",
        "2026-09-24",
        "DEPOSIT",
        500.00,
        "INR",
        "integrity_test"
    ))


# ============================================================
# TEST 2
# Account references nonexistent customer
# ============================================================

def test_nonexistent_customer(connection):

    connection.execute("""
        INSERT INTO accounts (
            account_id,
            customer_id,
            branch_id,
            account_type,
            account_status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "TEST-ACCOUNT-001",
        "NONEXISTENT-CUSTOMER",
        "BR001",
        "SAVINGS",
        "ACTIVE"
    ))


# ============================================================
# TEST 3
# Duplicate primary key
# ============================================================

def test_duplicate_primary_key(connection):

    # Get an existing account and its valid related values.
    existing_account = connection.execute("""
        SELECT account_id, customer_id, branch_id
        FROM accounts
        LIMIT 1
    """).fetchone()

    if existing_account is None:
        raise RuntimeError(
            "No existing account found for duplicate PK test."
        )

    connection.execute("""
        INSERT INTO accounts (
            account_id,
            customer_id,
            branch_id,
            account_type,
            account_status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        existing_account[0],  # Existing account_id -> duplicate PK
        existing_account[1],  # Valid customer_id
        existing_account[2],  # Valid branch_id
        "SAVINGS",
        "ACTIVE"
    ))


# ============================================================
# TEST 4
# Invalid transaction amount
# ============================================================

def test_invalid_amount(connection):

    # Get a valid account from the database.
    existing_account = connection.execute("""
        SELECT account_id
        FROM accounts
        LIMIT 1
    """).fetchone()

    if existing_account is None:
        raise RuntimeError(
            "No existing account found for amount test."
        )

    connection.execute("""
        INSERT INTO transactions (
            transaction_id,
            account_id,
            transaction_date,
            transaction_type,
            amount,
            currency,
            source_file
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEST-TXN-002",
        existing_account[0],
        "2026-09-24",
        "DEPOSIT",
        -50.00,
        "INR",
        "integrity_test"
    ))


# ============================================================
# TEST 5
# Missing required value
# ============================================================

def test_missing_required_value(connection):

    # Get a valid account so the failure we test is NOT the FK.
    existing_account = connection.execute("""
        SELECT account_id
        FROM accounts
        LIMIT 1
    """).fetchone()

    if existing_account is None:
        raise RuntimeError(
            "No existing account found for NOT NULL test."
        )

    connection.execute("""
        INSERT INTO transactions (
            transaction_id,
            account_id,
            transaction_date,
            transaction_type,
            amount,
            currency,
            source_file
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEST-TXN-003",
        existing_account[0],
        None,                 # transaction_date is NOT NULL
        "DEPOSIT",
        100.00,
        "INR",
        "integrity_test"
    ))


# ============================================================
# RUN ALL TESTS
# ============================================================

if __name__ == "__main__":

    # Create evidence directory if it does not exist.
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Open evidence file.
    with EVIDENCE_PATH.open("w", encoding="utf-8") as evidence_file:

        # Send all print() output to both terminal and file.
        original_stdout = sys.stdout
        sys.stdout = Tee(original_stdout, evidence_file)

        try:

            print("=" * 70)
            print("PART C - DATABASE INTEGRITY TEST RESULTS")
            print("=" * 70)

            run_test(
                "Transaction references nonexistent account",
                "FOREIGN KEY (transactions.account_id)",
                test_nonexistent_account
            )

            run_test(
                "Account references nonexistent customer",
                "FOREIGN KEY (accounts.customer_id)",
                test_nonexistent_customer
            )

            run_test(
                "Duplicate account primary key",
                "PRIMARY KEY (accounts.account_id)",
                test_duplicate_primary_key
            )

            run_test(
                "Transaction amount = -50",
                "CHECK (amount > 0)",
                test_invalid_amount
            )

            run_test(
                "Transaction missing required transaction_date",
                "NOT NULL (transactions.transaction_date)",
                test_missing_required_value
            )

            print("\n" + "=" * 70)
            print("INTEGRITY TESTING COMPLETE")
            print("=" * 70)

        finally:
            # Restore normal terminal output.
            sys.stdout = original_stdout

    print()
    print(f"Evidence saved to: {EVIDENCE_PATH}")