# Relational Banking Database

## 1. Project Overview

This project builds a relational banking database using **SQLite and Python**.

The database combines customer, branch, account, and transaction data into a structured relational model.

The project demonstrates:

- Relational database design
- Primary and foreign keys
- NOT NULL and CHECK constraints
- CSV data loading
- Database integrity testing
- SQL analysis using JOINs and aggregations
- CASE expressions
- Common Table Expressions (CTEs)
- Window functions
- Query-plan investigation
- Index creation and analysis
- Automated testing with pytest
- Database engineering documentation

The final database contains:

- **3 branches**
- **6 customers**
- **10 accounts**
- **10 valid transactions**

---

# 2. Architecture and Data Flow

The project follows this data flow:

```text
CSV Files
    |
    v
Python Loading Scripts
    |
    v
SQLite Database
    |
    +----> Integrity Constraints
    |
    +----> SQL Analysis
    |
    +----> Index Investigation
    |
    v
Pytest Tests
```

## Data Sources

The `data/` directory contains:

- `branches.csv`
- `customers.csv`
- `accounts.csv`
- `valid_transactions.csv`

The `valid_transactions.csv` file contains the valid transactions produced by the earlier data-validation pipeline.

## Database Flow

1. `schema.sql` defines the database tables and constraints.
2. `database.py` creates the SQLite database.
3. `load_data.py` loads CSV data into the database.
4. SQLite constraints protect relationships and data integrity.
5. `analysis.sql` contains SQL analysis queries.
6. `test_integrity.py` deliberately tests invalid database operations.
7. `test_database_behavior.py` tests actual database-building and loading behavior.
8. `test_index.py` compares query plans before and after index creation.

---

# 3. Folder Structure

```text
relational_banking_database/
│
├── data/
│   ├── branches.csv
│   ├── customers.csv
│   ├── accounts.csv
│   └── valid_transactions.csv
│
├── evidence/
│   ├── integrity_tests.txt
│   ├── sql_analysis_result.txt
│   └── index_query_plan.txt
│
├── sql/
│   └── analysis.sql
│
├── src/
│   ├── database.py
│   ├── schema.sql
│   ├── load_data.py
│   └── check_database.py
│
├── tests/
│   ├── test_database.py
│   ├── test_database_behavior.py
│   ├── test_integrity.py
│   ├── test_index.py
│   └── run_analysis.py
│
├── banking.db
└── README.md
```

---

# 4. ER Diagram

The database contains four main entities:

- Branches
- Customers
- Accounts
- Transactions

The relationships are:

```text
                    +----------------+
                    |    BRANCHES    |
                    +----------------+
                    | PK branch_id   |
                    | branch_name    |
                    | city           |
                    | state          |
                    +-------+--------+
                            |
                            | 1
                            |
                            | many
                            |
                    +-------v--------+
                    |    ACCOUNTS    |
                    +----------------+
                    | PK account_id  |
                    | FK customer_id |
                    | FK branch_id   |
                    | account_type   |
                    | account_status |
                    +-------+--------+
                            |
                            | 1
                            |
                            | many
                            |
                    +-------v---------+
                    |  TRANSACTIONS   |
                    +-----------------+
                    | PK transaction_id|
                    | FK account_id   |
                    | transaction_date|
                    | transaction_type|
                    | amount          |
                    | currency        |
                    | source_file     |
                    +-----------------+


+----------------+
|   CUSTOMERS    |
+----------------+
| PK customer_id |
| customer_name  |
| email          |
| customer_segment|
+-------+--------+
        |
        | 1
        |
        | many
        |
        +--------------------> ACCOUNTS
```

## Entity Relationships

### Branches → Accounts

One branch can have many accounts.

```text
branches.branch_id
        |
        | 1 : many
        v
accounts.branch_id
```

### Customers → Accounts

One customer can have many accounts.

```text
customers.customer_id
        |
        | 1 : many
        v
accounts.customer_id
```

### Accounts → Transactions

One account can have many transactions.

```text
accounts.account_id
        |
        | 1 : many
        v
transactions.account_id
```

---

# 5. Database Schema

## 5.1 Branches

The `branches` table stores information about banking branches.

### Primary Key

```text
branch_id
```

### Columns

| Column | Description |
|---|---|
| `branch_id` | Unique branch identifier |
| `branch_name` | Name of the branch |
| `city` | Branch city |
| `state` | Branch state |

The required branch information is protected using `NOT NULL` constraints.

---

## 5.2 Customers

The `customers` table stores customer information.

### Primary Key

```text
customer_id
```

### Columns

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `customer_name` | Customer name |
| `email` | Customer email |
| `customer_segment` | Customer segment |

---

## 5.3 Accounts

The `accounts` table stores bank account information.

### Primary Key

```text
account_id
```

### Foreign Keys

```text
customer_id -> customers.customer_id

branch_id -> branches.branch_id
```

### Columns

| Column | Description |
|---|---|
| `account_id` | Unique account identifier |
| `customer_id` | Customer owning the account |
| `branch_id` | Branch associated with the account |
| `account_type` | Type of account |
| `account_status` | Current account status |

The required fields are protected using `NOT NULL`.

---

## 5.4 Transactions

The `transactions` table stores banking transaction information.

### Primary Key

```text
transaction_id
```

### Foreign Key

```text
account_id -> accounts.account_id
```

### Columns

| Column | Description |
|---|---|
| `transaction_id` | Unique transaction identifier |
| `account_id` | Account associated with the transaction |
| `transaction_date` | Date of transaction |
| `transaction_type` | CREDIT or DEBIT |
| `amount` | Transaction amount |
| `currency` | Transaction currency |
| `source_file` | Source CSV file |

The transaction amount uses:

```sql
CHECK (amount > 0)
```

This prevents zero or negative transaction amounts.

---

# 6. Why Should Customer Information Not Be Repeated on Every Transaction?

Customer information should not be repeated in every transaction record because it creates unnecessary data duplication.

For example, if a customer has 1,000 transactions and the customer's name and email are stored in every transaction, the same information would be stored 1,000 times.

This creates several problems:

- Data redundancy
- Increased storage requirements
- Update anomalies
- Possible inconsistent customer information
- More difficult data maintenance

For example, if a customer's email address changes, storing the email in every transaction would require many transaction records to be updated.

If some records were updated and others were not, the database could contain different email addresses for the same customer.

Instead, this database stores customer information once in the `customers` table.

The relationship is:

```text
Customer
    |
    | customer_id
    v
Account
    |
    | account_id
    v
Transaction
```

A transaction therefore only needs to store `account_id`.

Customer information can be retrieved using SQL JOINs.

Example:

```sql
SELECT
    t.transaction_id,
    c.customer_name,
    c.email,
    t.amount
FROM transactions t
JOIN accounts a
    ON t.account_id = a.account_id
JOIN customers c
    ON a.customer_id = c.customer_id;
```

This design reduces duplication and keeps customer information in one place.

---

# 7. Python Validation vs Database Constraints

Python validation and database constraints both protect data quality, but they operate at different stages.

## Python Validation

Python validation occurs before data is inserted into the database.

The earlier transaction-validation pipeline can check things such as:

- Required columns
- Missing values
- Allowed transaction types
- Allowed currencies
- Invalid transaction records
- Other input-level validation rules

Invalid records can be separated from valid records before they are loaded into SQLite.

The general flow is:

```text
CSV Input
    |
    v
Python Validation
    |
    +------> Invalid Records
    |
    v
Valid Records
    |
    v
SQLite Database
```

## Database Constraints

Database constraints are enforced directly by SQLite.

This project uses:

- `PRIMARY KEY`
- `FOREIGN KEY`
- `NOT NULL`
- `CHECK`

For example:

```sql
amount REAL NOT NULL CHECK (amount > 0)
```

This means SQLite rejects a transaction with an amount less than or equal to zero.

Foreign keys also protect relationships:

```text
accounts.customer_id
        |
        v
customers.customer_id
```

and:

```text
transactions.account_id
        |
        v
accounts.account_id
```

## Main Difference

The main difference is:

```text
Python Validation
        |
        v
Validates incoming data before database insertion


Database Constraint
        |
        v
Protects data integrity inside the database
```

Python validation is useful for identifying and handling invalid input data.

Database constraints provide another layer of protection at the database level.

Using both provides stronger data-integrity protection.

---

# 8. Foreign-Key Enforcement

Foreign-key enforcement ensures that relationships between related tables remain valid.

This project enables:

```sql
PRAGMA foreign_keys = ON;
```

Foreign-key enforcement is also enabled in the Python database connection.

## Example

A transaction contains:

```text
account_id
```

That account must exist in the `accounts` table.

```text
transactions.account_id
        |
        v
accounts.account_id
```

Similarly, an account must reference an existing customer:

```text
accounts.customer_id
        |
        v
customers.customer_id
```

And an account must reference an existing branch:

```text
accounts.branch_id
        |
        v
branches.branch_id
```

---

# 9. What Could Happen If Foreign-Key Enforcement Were Disabled?

If foreign-key enforcement were disabled, SQLite could allow records that reference nonexistent parent records.

For example, suppose a transaction contains:

```text
transaction_id = T9999
account_id     = A9999
```

but `A9999` does not exist in the `accounts` table.

Without foreign-key enforcement, such an orphan transaction could potentially be inserted.

This could result in:

- Broken relationships
- Orphan transactions
- Accounts referencing nonexistent customers
- Incorrect JOIN results
- Incorrect analytical results
- Reduced confidence in database integrity

For example:

```text
Transaction
     |
     | account_id = A9999
     |
     X
Account A9999 does not exist
```

This is why the project explicitly enables:

```sql
PRAGMA foreign_keys = ON;
```

The project also includes integrity tests that deliberately attempt invalid foreign-key operations and verify that SQLite rejects them.

---

# 10. Data Integrity Strategy

The project uses multiple layers of data-integrity protection.

## Primary Keys

Primary keys uniquely identify records.

Examples:

```text
branch_id
customer_id
account_id
transaction_id
```

Duplicate primary-key values are rejected by SQLite.

## Foreign Keys

Foreign keys maintain relationships between tables.

```text
accounts.customer_id
        |
        v
customers.customer_id
```

```text
accounts.branch_id
        |
        v
branches.branch_id
```

```text
transactions.account_id
        |
        v
accounts.account_id
```

## NOT NULL

Required fields cannot contain NULL values.

For example:

```text
branch_name
customer_name
account_id
transaction_date
amount
currency
```

## CHECK Constraint

Transaction amounts must be greater than zero:

```sql
CHECK (amount > 0)
```

## Integrity Testing

The project deliberately tests invalid operations such as:

- Transaction referencing a nonexistent account
- Account referencing a nonexistent customer
- Duplicate primary key
- Negative transaction amount
- Missing required transaction date

These tests demonstrate that SQLite actually rejects invalid records.

Evidence is stored in:

```text
evidence/integrity_tests.txt
```

---

# 11. Database Build and Load

The database can be created using the production database script.

From the project root:

```powershell
python src/database.py
```

This creates the database tables using:

```text
src/schema.sql
```

The data can then be loaded using:

```powershell
python src/load_data.py
```

The loading process reads:

```text
data/branches.csv
data/customers.csv
data/accounts.csv
data/valid_transactions.csv
```

The expected final row counts are:

```text
branches: 3
customers: 6
accounts: 10
transactions: 10
```

---

# 12. Checking the Database

The database can be checked using:

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

This provides a quick verification that the database contains the expected data.

---

# 13. Running Tests

## Install pytest

If pytest is not installed:

```powershell
python -m pip install pytest
```

Check the installed version:

```powershell
python -m pytest --version
```

---

## Part B Database Tests

Run:

```powershell
python -m pytest -q tests/test_database.py
```

These tests verify:

- Database connection
- Foreign-key enforcement
- Required tables
- Expected row counts

---

## Part C Integrity Tests

Run:

```powershell
python tests/test_integrity.py
```

These tests deliberately attempt invalid database operations.

The evidence is stored in:

```text
evidence/integrity_tests.txt
```

---

## Part F Database Behavior Tests

Run:

```powershell
python -m pytest -q tests/test_database_behavior.py
```

The Part F test suite contains seven meaningful tests covering:

1. Required tables
2. Foreign-key enforcement
3. Expected row counts
4. Invalid foreign-key rejection
5. Invalid transaction amount rejection
6. Important SQL analysis result
7. Database rebuild/load rerun behavior

The current test result is:

```text
7 passed
```

---

## Run All Pytest Tests

To run all pytest-based tests:

```powershell
python -m pytest -q
```

---

# 14. SQL Analysis

SQL analysis queries are stored in:

```text
sql/analysis.sql
```

The project contains 14 SQL queries.

The analysis covers the required SQL concepts:

- JOINs
- Aggregation
- CASE expressions
- Common Table Expressions (CTEs)
- Window functions
- Business questions

## SQL Analysis Categories

The analysis includes:

1. Transaction details with customer, account, and branch information
2. Accounts by customer
3. Transactions by branch
4. Transaction count by customer
5. Total transaction amount by customer
6. Transaction count by branch
7. Transaction type totals and averages
8. Transaction amount bands using CASE
9. Customer totals using a CTE
10. Ranking transactions within customers using a window function
11. Running totals using a window function
12. Ranking customers by transaction value
13. Branch transaction-value analysis
14. Transaction-type value analysis

The SQL results are stored in:

```text
evidence/sql_analysis_result.txt
```

---

# 15. SQL Analysis Examples

## JOIN Example

The project uses JOINs to combine transaction information with account, customer, and branch information.

Example:

```sql
SELECT
    t.transaction_id,
    c.customer_name,
    a.account_id,
    b.branch_name,
    t.transaction_date,
    t.transaction_type,
    t.amount
FROM transactions t
JOIN accounts a
    ON t.account_id = a.account_id
JOIN customers c
    ON a.customer_id = c.customer_id
JOIN branches b
    ON a.branch_id = b.branch_id;
```

## Aggregation Example

Transaction totals can be grouped by customer:

```sql
SELECT
    c.customer_name,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(t.amount) AS total_amount
FROM customers c
JOIN accounts a
    ON c.customer_id = a.customer_id
JOIN transactions t
    ON a.account_id = t.account_id
GROUP BY c.customer_id, c.customer_name;
```

## CASE Example

Transaction amounts can be grouped into bands:

```sql
CASE
    WHEN amount < 100 THEN 'Small'
    WHEN amount < 500 THEN 'Medium'
    ELSE 'Large'
END
```

## CTE Example

A Common Table Expression can first calculate customer totals and then filter the results.

```sql
WITH customer_totals AS (
    SELECT
        c.customer_id,
        c.customer_name,
        SUM(t.amount) AS total_amount
    FROM customers c
    JOIN accounts a
        ON c.customer_id = a.customer_id
    JOIN transactions t
        ON a.account_id = t.account_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT *
FROM customer_totals
WHERE total_amount >= 500;
```

## Window Function Example

A window function can rank transactions within each customer:

```sql
RANK() OVER (
    PARTITION BY customer_id
    ORDER BY amount DESC
)
```

Window functions allow calculations across related rows without collapsing the result into one row per group.

---

# 16. Index Investigation

The project investigates query performance using:

```sql
EXPLAIN QUERY PLAN
```

A realistic transaction lookup was selected using `account_id`.

Example query:

```sql
SELECT
    transaction_id,
    transaction_date,
    transaction_type,
    amount,
    currency
FROM transactions
WHERE account_id = 'A1001'
ORDER BY transaction_date;
```

---

## Before Index

Before creating the index, the query plan showed:

```text
SCAN transactions
```

This indicates that SQLite was scanning the transactions table to find matching rows.

The query plan also showed:

```text
USE TEMP B-TREE FOR ORDER BY
```

because the existing access path did not directly satisfy the requested ordering.

---

## Index Creation

The project created the following index:

```sql
CREATE INDEX idx_transactions_account_id
ON transactions(account_id);
```

The index is appropriate because `account_id` is used as a lookup/filter field in the investigated query.

---

## After Index

After creating the index, the query plan showed:

```text
SEARCH transactions USING INDEX idx_transactions_account_id
```

This indicates that SQLite changed the lookup strategy from a table scan to an index-based search.

The query plan still showed:

```text
USE TEMP B-TREE FOR ORDER BY
```

because the created index is on `account_id`, while the query also orders by `transaction_date`.

---

## Query Plan Limitation

The dataset in this project is small.

Therefore, the query-plan change demonstrates a change in SQLite's access strategy, but it does not by itself prove a measurable real-world performance improvement.

The evidence is stored in:

```text
evidence/index_query_plan.txt
```

---

# 17. Why Might Adding Indexes to Every Column Be a Bad Idea?

Indexes can improve query performance, but adding indexes to every column is not automatically beneficial.

Indexes require additional storage and must be maintained when data changes.

For example, when a row is inserted, updated, or deleted, SQLite may also need to update the relevant indexes.

Too many unnecessary indexes can therefore result in:

- Increased storage usage
- Additional maintenance overhead
- Slower INSERT operations
- Slower UPDATE operations
- Slower DELETE operations
- More complicated database design

Indexes should instead be created based on actual query patterns.

Useful candidates are often columns that are frequently used for:

- Searching
- Filtering
- JOIN operations
- Sorting

In this project, the investigated index is:

```sql
CREATE INDEX idx_transactions_account_id
ON transactions(account_id);
```

because `account_id` is used for a realistic transaction lookup.

---

# 18. Relational Banking Database vs Analytical Data Warehouse

This project uses a relational banking database designed around operational entities:

```text
Customers
    |
    v
Accounts
    |
    v
Transactions

Branches
    |
    v
Accounts
```

The database uses normalized tables, primary keys, foreign keys, and constraints to maintain relationships and data integrity.

The main purpose is to maintain structured and consistent banking data.

An analytical data warehouse is generally designed for reporting and analytical workloads.

A warehouse may organize information using fact and dimension tables, for example:

```text
             +------------------+
             | Transaction Fact |
             +------------------+
                /      |      \
               /       |       \
              v        v        v
        Customer    Account    Branch
        Dimension  Dimension  Dimension
```

The warehouse structure is designed to make large-scale reporting, aggregation, and historical analysis easier.

Therefore, one key difference is:

```text
Relational Banking Database
    |
    +-- Operational data
    +-- Normalized relationships
    +-- Strong data integrity
    +-- Primary/foreign keys


Analytical Data Warehouse
    |
    +-- Analytical/reporting workloads
    +-- Fact and dimension structures
    +-- Large-scale aggregation
    +-- Historical analysis
```

In short, this project focuses on maintaining relational banking data and its integrity, while an analytical data warehouse is primarily designed for reporting and analytical workloads.

---

# 19. Assumptions

The project makes the following assumptions:

1. Each customer has a unique `customer_id`.
2. Each account has a unique `account_id`.
3. Each branch has a unique `branch_id`.
4. Each transaction has a unique `transaction_id`.
5. Every account belongs to an existing customer.
6. Every account belongs to an existing branch.
7. Every transaction belongs to an existing account.
8. Transaction amounts must be greater than zero.
9. The supplied CSV files contain the expected columns.
10. `valid_transactions.csv` contains transactions that passed the earlier validation process.
11. SQLite is sufficient for the local scope of this assignment.
12. The database is intended for demonstration and learning rather than production banking operations.

---

# 20. Known Limitations

The project has several limitations:

1. The database uses SQLite and is intended for a local assignment environment.
2. The dataset is small, so query-plan investigation does not demonstrate large-scale performance improvements.
3. Transaction dates are stored as text.
4. The schema does not implement advanced banking functionality such as account balances, transfers, interest calculations, or detailed audit history.
5. The database rebuild process recreates the schema before loading data.
6. The project does not represent a production banking system.
7. The project does not include authentication or authorization because the focus is relational database design and analysis.
8. The current index investigation focuses on the specific `account_id` lookup rather than comprehensive database performance benchmarking.

---

# 21. Evidence

The `evidence/` directory contains supporting outputs from the project.

## Integrity Test Evidence

```text
evidence/integrity_tests.txt
```

Contains evidence of deliberately attempted invalid database operations and the resulting constraint failures.

## SQL Analysis Evidence

```text
evidence/sql_analysis_result.txt
```

Contains the SQL queries and their returned results.

## Index Investigation Evidence

```text
evidence/index_query_plan.txt
```

Contains the query plan before and after creating the transaction `account_id` index.

---

# 22. Final Project Summary

This project demonstrates a complete relational database engineering workflow:

```text
CSV Data
    |
    v
Python Validation
    |
    v
Valid Transaction Data
    |
    v
SQLite Schema
    |
    v
Database Loading
    |
    v
Integrity Constraints
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

The final database contains:

```text
3 branches
6 customers
10 accounts
10 valid transactions
```

The project demonstrates:

- Relational database modeling
- Entity relationships
- Primary keys
- Foreign keys
- NOT NULL constraints
- CHECK constraints
- CSV-to-database loading
- Data integrity testing
- SQL JOINs
- Aggregations
- CASE expressions
- CTEs
- Window functions
- Business-oriented SQL analysis
- EXPLAIN QUERY PLAN
- Index investigation
- pytest-based automated testing
- Database engineering documentation

---

# 23. Conclusion

The project provides a complete example of how validated banking data can be transformed into a structured relational database.

The design separates customers, branches, accounts, and transactions into related tables instead of duplicating information.

Database constraints provide protection at the storage layer, while Python validation helps identify invalid input before loading.

SQL analysis provides business and relational insights, while the index investigation demonstrates how database access strategies can change based on indexing.

Automated pytest tests verify important database behaviors and ensure that the database-building and loading process works as expected.
