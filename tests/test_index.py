import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database path
DATABASE_PATH = BASE_DIR / "banking.db"

# Evidence file path
EVIDENCE_PATH = BASE_DIR / "evidence" / "index_query_plan.txt"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def main():
    connection = get_connection()

    try:
        query = """
        SELECT
            transaction_id,
            transaction_date,
            transaction_type,
            amount,
            currency
        FROM transactions
        WHERE account_id = 'A1001'
        ORDER BY transaction_date;
        """

        output = []

        output.append("=" * 60)
        output.append("PART E - INDEX AND QUERY PLAN INVESTIGATION")
        output.append("=" * 60)

        output.append("\nSELECTED QUERY")
        output.append("-" * 60)
        output.append(query.strip())

        # --------------------------------------------------
        # REMOVE EXISTING INDEX
        # --------------------------------------------------

        connection.execute("""
            DROP INDEX IF EXISTS idx_transactions_account_id;
        """)

        connection.commit()

        # --------------------------------------------------
        # BEFORE INDEX
        # --------------------------------------------------

        output.append("\nBEFORE INDEX")
        output.append("-" * 60)

        plan_before = connection.execute(
            "EXPLAIN QUERY PLAN " + query
        ).fetchall()

        for row in plan_before:
            print(row)
            output.append(str(row))

        # --------------------------------------------------
        # CREATE INDEX
        # --------------------------------------------------

        output.append("\nCREATING INDEX")
        output.append("-" * 60)

        connection.execute("""
            CREATE INDEX idx_transactions_account_id
            ON transactions(account_id);
        """)

        connection.commit()

        print("PASS: Index created successfully")
        output.append("PASS: Index created successfully")

        # --------------------------------------------------
        # AFTER INDEX
        # --------------------------------------------------

        output.append("\nAFTER INDEX")
        output.append("-" * 60)

        plan_after = connection.execute(
            "EXPLAIN QUERY PLAN " + query
        ).fetchall()

        for row in plan_after:
            print(row)
            output.append(str(row))

        # --------------------------------------------------
        # COMPARISON
        # --------------------------------------------------

        output.append("\nCOMPARISON")
        output.append("-" * 60)

        output.append("Before index:")
        output.append(str(plan_before))

        output.append("\nAfter index:")
        output.append(str(plan_after))

        output.append(
            "\nThe query plan changed from a table scan to an "
            "index-based search using idx_transactions_account_id."
        )

        output.append(
            "The USE TEMP B-TREE FOR ORDER BY operation remained "
            "because the index is on account_id and not transaction_date."
        )

        # --------------------------------------------------
        # NOTE
        # --------------------------------------------------

        output.append("\nNOTE")
        output.append("-" * 60)

        output.append(
            "The database contains a very small number of transaction "
            "records. Therefore, this query-plan change does not prove "
            "a measurable performance improvement."
        )

        output.append(
            "The purpose of this investigation is to demonstrate how "
            "an index can change SQLite's query execution strategy."
        )

        # --------------------------------------------------
        # SAVE EVIDENCE
        # --------------------------------------------------

        EVIDENCE_PATH.parent.mkdir(exist_ok=True)

        with open(EVIDENCE_PATH, "w", encoding="utf-8") as file:
            file.write("\n".join(output))

        print("\nEvidence saved successfully:")
        print(EVIDENCE_PATH)

    finally:
        connection.close()


if __name__ == "__main__":
    main()