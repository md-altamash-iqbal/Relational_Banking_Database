import csv
from pathlib import Path

from database import get_connection, DATABASE_PATH


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_branches(connection):
    """Load branch data into the branches table."""

    file_path = DATA_DIR / "branches.csv"

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sql = """
                INSERT INTO branches (
                    branch_id,
                    branch_name,
                    city,
                    state
                )
                VALUES (?, ?, ?, ?)
            """

            values = (
                row["branch_id"],
                row["branch_name"],
                row["city"],
                row["state"],
            )

            connection.execute(sql, values)

    print("Branches loaded successfully.")


def load_customers(connection):
    """Load customer data into the customers table."""

    file_path = DATA_DIR / "customers.csv"

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sql = """
                INSERT INTO customers (
                    customer_id,
                    customer_name,
                    email,
                    customer_segment
                )
                VALUES (?, ?, ?, ?)
            """

            values = (
                row["customer_id"],
                row["customer_name"],
                row["email"],
                row["customer_segment"],
            )

            connection.execute(sql, values)

    print("Customers loaded successfully.")


def load_accounts(connection):
    """Load account data into the accounts table."""

    file_path = DATA_DIR / "accounts.csv"

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sql = """
                INSERT INTO accounts (
                    account_id,
                    customer_id,
                    branch_id,
                    account_type,
                    account_status
                )
                VALUES (?, ?, ?, ?, ?)
            """

            values = (
                row["account_id"],
                row["customer_id"],
                row["branch_id"],
                row["account_type"],
                row["account_status"],
            )

            connection.execute(sql, values)

    print("Accounts loaded successfully.")


def load_transactions(connection):
    """Load valid transaction data into the transactions table."""

    file_path = DATA_DIR / "valid_transactions.csv"

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sql = """
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
            """

            values = (
                row["transaction_id"],
                row["account_id"],
                row["transaction_date"],
                row["transaction_type"],
                float(row["amount"]),
                row["currency"],
                row.get("source_file"),
            )

            connection.execute(sql, values)

    print("Transactions loaded successfully.")


def load_all_data(database_path=DATABASE_PATH):
    """Load all CSV files into the SQLite database."""

    connection = get_connection(database_path)

    try:
        load_branches(connection)
        load_customers(connection)
        load_accounts(connection)
        load_transactions(connection)

        connection.commit()

        print("\nAll data loaded successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    load_all_data()