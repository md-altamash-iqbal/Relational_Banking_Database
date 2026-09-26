# Relational Banking Database

## Project Overview

This project builds a relational banking database using **SQLite and Python**.

The database stores:

- Customers
- Branches
- Accounts
- Transactions

The project demonstrates:

- Relational database design
- Primary and foreign keys
- Database constraints
- CSV data loading
- SQL analysis
- CTEs and window functions
- Query-plan investigation
- Indexing
- Database integrity testing
- Automated testing with pytest

The database is built using the supplied reference CSV files and the valid transactions generated from the Week 3 transaction pipeline.

---

## Architecture and Data Flow

The project follows this flow:

```text
CSV Files
   |
   v
Python CSV Loader
   |
   v
SQLite Database
   |
   +-- branches
   +-- customers
   +-- accounts
   +-- transactions
   |
   +-- SQL Analysis
   +-- Integrity Testing
   +-- Query Plan / Index Investigation
```

`src/database.py` creates the database and applies the schema defined in `src/schema.sql`.

`src/load_data.py` loads the supplied CSV files into the database.

The resulting `banking.db` is used for SQL analysis, integrity checks, and automated tests.

---

## Project Structure

```text
relational_banking_database/
|
+-- data/
|   +-- customers.csv
|   +-- branches.csv
|   +-- accounts.csv
|   +-- valid_transactions.csv
|
+-- evidence/
|   +-- integrity_tests.txt
|   +-- sql_analysis_result.txt
|   +-- index_query_plan.txt
|
+-- sql/
|   +-- analysis.sql
|
+-- src/
|   +-- database.py
|   +-- load_data.py
|   +-- check_database.py
|   +-- schema.sql
|
+-- tests/
|   +-- test_database.py
|   +-- test_database_behavior.py
|   +-- test_integrity.py
|   +-- test_index.py
|   +-- run_analysis.py
|
+-- banking.db
+-- README.md
```

---

## Database Schema

The database contains four related tables.

### Branches

Stores bank branch information.

- `branch_id` - Primary Key
- `branch_name`
- `city`
- `state`

### Customers

Stores customer information.

- `customer_id` - Primary Key
- `customer_name`
- `email`
- `customer_segment`

### Accounts

Stores customer accounts.

- `account_id` - Primary Key
- `customer_id` - Foreign Key
- `branch_id` - Foreign Key
- `account_type`
- `account_status`

### Transactions

Stores banking transactions.

- `transaction_id` - Primary Key
- `account_id` - Foreign Key
- `transaction_date`
- `transaction_type`
- `amount`
- `currency`
- `source_file`

### Relationships

```text
CUSTOMERS
    |
    | 1
    |
    | many
    v
ACCOUNTS <---- BRANCHES
    |
    | 1
    |
    | many
    v
TRANSACTIONS
```

Each account belongs to one customer and one branch.

Each transaction belongs to one account.

---

## ER Diagram

The ER diagram represents the relationships between customers, branches, accounts, and transactions.

```text
CUSTOMERS
    |
    v
ACCOUNTS <---- BRANCHES
    |
    v
TRANSACTIONS
```

The database uses primary keys and foreign keys to maintain these relationships.

---

## Data Integrity

The database uses several constraints to protect data quality.

### Primary Keys

Primary keys prevent duplicate identifiers.

### Foreign Keys

Foreign keys ensure that related records exist.

For example, a transaction cannot reference an account that does not exist.

### NOT NULL

Required fields cannot contain `NULL` values.

### CHECK

Transaction amounts must be positive:

```sql
CHECK (amount > 0)
```

Foreign-key enforcement is explicitly enabled for every SQLite connection:

```python
connection.execute("PRAGMA foreign_keys = ON")
```

---

## Why Customer Information Is Not Repeated

Customer information is stored once in the `customers` table instead of being repeated in every transaction.

A transaction stores an `account_id`, and the account references the customer.

This reduces:

- Data duplication
- Storage requirements
- Update inconsistencies

It also keeps the database normalized and maintains relationships through primary and foreign keys.

---

## Python Validation vs Database Constraints

Python validation checks data before it reaches the database.

Database constraints provide a second layer of protection directly inside SQLite.

For example, Python can validate that a transaction amount is positive before insertion:

```python
if amount <= 0:
    # reject invalid data
```

The database also enforces the rule:

```sql
CHECK (amount > 0)
```

Python validation helps prevent invalid data from reaching the database, while database constraints provide database-level protection regardless of which application or operation attempts the insert.

---

## Building the Database

From the project root, run:

```powershell
python src/database.py
```

The database schema is created using:

```text
src/schema.sql
```

Load the CSV data using:

```powershell
python src/load_data.py
```

The expected database row counts are:

```text
branches: 3
customers: 6
accounts: 10
transactions: 10
```

The Week 3 pipeline produced 10 valid transactions, which are loaded into the database.

### Rebuilding the Database

The database can be rebuilt from the schema and supplied CSV files.

The schema creation process drops the existing tables and recreates them before loading the data.

This prevents duplicate records when performing a complete rebuild.

---

## Checking the Database

Run:

```powershell
python src/check_database.py
```

Expected row counts:

```text
branches: 3
customers: 6
accounts: 10
transactions: 10
```

---

## Testing

The project uses **pytest** for automated database behavior testing.

Run the database behavior tests with:

```powershell
python -m pytest -q tests/test_database_behavior.py
```

The test suite covers:

- Required database tables
- Foreign-key enforcement
- Expected row counts
- Invalid foreign-key rejection
- Invalid transaction amount rejection
- Important SQL result
- Database rebuild and reload behavior

The completed database behavior test suite contains **7 meaningful tests**.

---

## Integrity Testing

Deliberate integrity-failure tests are included in:

```text
tests/test_integrity.py
```

The tests cover:

- Transaction referencing a nonexistent account
- Account referencing a nonexistent customer
- Duplicate primary key
- Invalid transaction amount
- Missing required transaction date

These tests verify that SQLite rejects invalid records using the appropriate database constraints.

Evidence is stored in:

```text
evidence/integrity_tests.txt
```

---

## SQL Analysis

SQL analysis is stored in:

```text
sql/analysis.sql
```

The project contains **14 SQL analysis queries** covering:

- JOINs
- Aggregation
- `COUNT()`
- `SUM()`
- `AVG()`
- `GROUP BY`
- `CASE`
- Common Table Expressions (CTEs)
- Window functions
- Running totals
- Ranking
- Customer analysis
- Branch analysis
- Transaction-type analysis
- Business questions

### Example Business Question

**Which branch has the highest total transaction value?**

For the supplied data:

```text
BR003 - Lake Branch
Total transaction value: 1575.0
```

SQL execution evidence is stored in:

```text
evidence/sql_analysis_result.txt
```

---

## Index Investigation

An index was investigated for queries filtering transactions by `account_id`.

The query pattern investigated was:

```sql
EXPLAIN QUERY PLAN
SELECT
    transaction_id,
    amount,
    transaction_date
FROM transactions
WHERE account_id = 'A1001';
```

### Before Index

SQLite reported:

```text
SCAN transactions
```

This indicates that SQLite scanned the transactions table to find matching rows.

### Index Created

```sql
CREATE INDEX idx_transactions_account_id
ON transactions(account_id);
```

### After Index

SQLite reported:

```text
SEARCH transactions USING INDEX idx_transactions_account_id (account_id=?)
```

This shows that SQLite changed the query plan to use the index for the `account_id` lookup.

Run the investigation with:

```powershell
python tests/test_index.py
```

Evidence is stored in:

```text
evidence/index_query_plan.txt
```

The query plan demonstrates a change in SQLite's execution strategy. It does not prove a specific execution-time improvement.

Because this project contains only a small number of rows, the index investigation demonstrates query-planning behavior rather than providing a meaningful performance benchmark.

---

## What Happens If Foreign Keys Are Disabled?

If foreign-key enforcement is disabled, SQLite can allow records to reference records that do not exist.

For example, a transaction could reference:

```text
account_id = A9999
```

even if that account does not exist.

This can create orphaned records and make relationships between tables unreliable.

Therefore, the project explicitly enables:

```sql
PRAGMA foreign_keys = ON;
```

for database connections.

---

## Why Not Add an Index to Every Column?

Indexes can improve the performance of some queries, but they also require:

- Additional storage
- Maintenance during INSERT operations
- Maintenance during UPDATE operations
- Maintenance during DELETE operations

Adding indexes to columns that are rarely used for filtering, joining, or ordering may provide little benefit while increasing storage and write overhead.

Indexes should therefore be created based on actual query patterns and database requirements.

---

## Relational Database vs Analytical Warehouse

This project uses a relational database designed to maintain operational data and relationships between customers, branches, accounts, and transactions.

An analytical data warehouse is primarily designed for large-scale historical analysis and reporting.

In simple terms:

```text
Relational Database
- Operational data
- Relationships
- Data integrity
- Transaction processing

Analytical Data Warehouse
- Historical analysis
- Reporting
- Large analytical queries
- Business intelligence
- Aggregated analysis
```

The relational database focuses on structured operational data and integrity, while a data warehouse focuses on analytical workloads and reporting.

---

## Assumptions

- Customer, branch, account, and transaction IDs are unique.
- Each account belongs to one customer and one branch.
- Each transaction belongs to one account.
- Transaction amounts must be greater than zero.
- Valid transaction types follow the Week 3 validation rules.
- The supplied reference CSV files are treated as authoritative.
- Transaction dates are stored as SQLite `TEXT` values.
- The database contains the valid Week 3 transaction records.
- `source_file` is retained for transaction data provenance.

---

## Limitations

- The database contains a small sample dataset.
- Query performance cannot be meaningfully benchmarked with this dataset.
- The database is rebuilt from the supplied CSV files rather than incrementally updated.
- Transaction dates are stored as text because SQLite does not provide a dedicated date data type.
- The schema is designed for this assignment and is not a complete production banking system.

---

## Evidence

The project includes evidence for database validation, SQL analysis, and index investigation.

```text
evidence/
|
+-- integrity_tests.txt
+-- sql_analysis_result.txt
+-- index_query_plan.txt
```

These files document:

- Deliberate integrity failures
- SQL query results
- Before/after query plans
- Index investigation

---

## Technologies Used

- Python
- SQLite
- SQL
- pytest
- CSV
- Git
- GitHub

---

## Final Database Result

The completed database contains:

```text
Branches:       3
Customers:      6
Accounts:      10
Transactions:  10
```

The project demonstrates a complete relational database workflow:

```text
Database Design
      |
      v
Schema Creation
      |
      v
CSV Data Loading
      |
      v
Integrity Enforcement
      |
      v
SQL Analysis
      |
      v
Index Investigation
      |
      v
Automated Testing
      |
      v
Documentation
```

## Conclusion

This project demonstrates how a relational banking database can be designed, implemented, populated, validated, analyzed, tested, and documented using Python and SQLite.
