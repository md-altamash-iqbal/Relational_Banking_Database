PRAGMA foreign_keys = ON;


DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS branches;


-- ============================================
-- Branch Table
-- ============================================

CREATE TABLE branches (
    branch_id TEXT PRIMARY KEY,
    branch_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL
);


-- ============================================
-- Customer Table
-- ============================================

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    customer_segment TEXT
);


-- ============================================
-- Account Table
-- ============================================

CREATE TABLE accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    branch_id TEXT NOT NULL,
    account_type TEXT NOT NULL,
    account_status TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id)
);


-- ============================================
-- Transaction Table
-- ============================================

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    currency TEXT NOT NULL,
    source_file TEXT,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
);