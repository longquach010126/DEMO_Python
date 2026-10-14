"""Kết nối và khởi tạo cơ sở dữ liệu SQLite."""
import os
import sqlite3
from contextlib import closing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "data")
# Có thể đổi file dữ liệu bằng biến môi trường FINANCE_DB (dùng khi chạy thử/kiểm thử).
DB_FILE = os.environ.get("FINANCE_DB") or os.path.join(DB_DIR, "finance.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    note TEXT,
    account TEXT DEFAULT 'Ví tiền mặt'
);
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    icon TEXT,
    color TEXT
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    icon TEXT
);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
"""


def connect():
    return sqlite3.connect(DB_FILE)


def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with closing(connect()) as conn, conn:
        conn.executescript(SCHEMA)

        # Nâng cấp CSDL cũ: thêm cột phương thức thanh toán nếu chưa có.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(transactions)")}

        # Nâng cấp CSDL cũ: thêm cột tài khoản nếu chưa có.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(transactions)")}
        if "account" not in columns:
            conn.execute("ALTER TABLE transactions ADD COLUMN account TEXT DEFAULT 'Ví tiền mặt'")

        if "method" not in columns:
            conn.execute("ALTER TABLE transactions ADD COLUMN method TEXT DEFAULT 'Tiền mặt'")

        # Nạp danh mục mặc định ở lần chạy đầu tiên.
        if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
            from theme import EXPENSE_CATEGORIES, INCOME_CATEGORIES
            rows = [(name, "Chi", icon, color) for name, (icon, color) in EXPENSE_CATEGORIES.items()]
            rows += [(name, "Thu", icon, color) for name, (icon, color) in INCOME_CATEGORIES.items()]
            conn.executemany("INSERT INTO categories (name, type, icon, color) VALUES (?, ?, ?, ?)", rows)

        # Nạp tài khoản mặc định
        if conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0:
            default_accounts = [
                ("Ví tiền mặt", "Tiền mặt", "💵"),
                ("Tài khoản ngân hàng", "Ngân hàng", "🏦")
            ]
            conn.executemany("INSERT INTO accounts (name, type, icon) VALUES (?, ?, ?)", default_accounts)


def execute_query(query, params=()):
    """Chạy câu lệnh ghi dữ liệu, trả về id của dòng vừa thêm (nếu có)."""
    with closing(connect()) as conn, conn:
        cursor = conn.execute(query, params)
        return cursor.lastrowid


def execute_many(query, rows):
    with closing(connect()) as conn, conn:
        conn.executemany(query, rows)


def fetch_query(query, params=()):
    with closing(connect()) as conn:
        return conn.execute(query, params).fetchall()
