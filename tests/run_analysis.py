import sqlite3
from pathlib import Path


DB_PATH = Path("banking.db")
SQL_PATH = Path("sql/analysis.sql")
OUTPUT_PATH = Path("evidence/sql_analysis_result.txt")


def main():
    connection = sqlite3.connect(DB_PATH)

    sql_text = SQL_PATH.read_text(encoding="utf-8")

    # Split the SQL file into individual statements.
    queries = [
        query.strip()
        for query in sql_text.split(";")
        if query.strip()
    ]

    output_lines = []

    output_lines.append("=" * 80)
    output_lines.append("PART D - SQL ANALYSIS RESULTS")
    output_lines.append("=" * 80)
    output_lines.append("")

    for number, query in enumerate(queries, start=1):

        output_lines.append("=" * 80)
        output_lines.append(f"QUERY {number}")
        output_lines.append("=" * 80)

        output_lines.append("\nSQL:")
        output_lines.append(query + ";")

        cursor = connection.execute(query)

        # Get column names
        columns = [description[0] for description in cursor.description]

        output_lines.append("\nRESULT:")
        output_lines.append(" | ".join(columns))
        output_lines.append("-" * 80)

        rows = cursor.fetchall()

        if rows:
            for row in rows:
                output_lines.append(
                    " | ".join(str(value) for value in row)
                )
        else:
            output_lines.append("(No rows returned)")

        output_lines.append("")

    connection.close()

    # Print results to terminal
    result = "\n".join(output_lines)
    print(result)

    # Save results to evidence file
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(result, encoding="utf-8")

    print("\nResults saved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()