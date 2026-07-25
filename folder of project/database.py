import sqlite3

conn = sqlite3.connect("expenses.db")
conn.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount INTEGER
)
""")
conn.close()