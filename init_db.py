import sqlite3

DB_FILE = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            category TEXT,
            amount REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
import subprocess


def add_expense(self):

    subprocess.run(["python", "visualize.py"])

    self.send_response(303)
    self.send_header("Location", "/")
    self.end_headers()
