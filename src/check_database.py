from database import get_connection


def show_row_counts():
    connection = get_connection()

    try:
        tables = [
            "branches",
            "customers",
            "accounts",
            "transactions",
        ]

        print("\nRow counts:")

        for table in tables:
            cursor = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            count = cursor.fetchone()[0]

            print(f"{table}: {count}")

    finally:
        connection.close()


if __name__ == "__main__":
    show_row_counts()