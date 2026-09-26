# Relational Banking Database

## 1. Project Overview

This project builds a relational banking database using SQLite and Python.

The database combines customer, branch, account, and transaction data into a structured relational model.

The project demonstrates:

- Relational database design
- Primary and foreign keys
- NOT NULL and CHECK constraints
- CSV data loading
- Database integrity testing
- SQL analysis using JOINs and aggregations
- CASE expressions
- CTEs
- Window functions
- Query-plan investigation
- Index creation and analysis
- Automated testing with pytest


---

# 2. Architecture and Data Flow

The project follows this basic data flow:

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


### Data Sources

The `data/` directory contains:

- `branches.csv`
- `customers.csv`
- `accounts.csv`
- `valid_transactions.csv`

The transaction file contains the valid transactions produced by the earlier data-validation pipeline.


### Database Flow

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
