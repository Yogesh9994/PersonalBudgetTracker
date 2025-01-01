import sqlite3
import subprocess
import urllib.parse

DB_FILE = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            type TEXT,
            amount REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_record(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode()
    data = urllib.parse.parse_qs(post_data)

    category = data['category'][0]
    record_type = data['type'][0]
    amount = float(data['amount'][0])
    date = data['date'][0]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO records (category, type, amount, date) VALUES (?, ?, ?, ?)",
                   (category, record_type, amount, date))
    conn.commit()
    conn.close()

    subprocess.run(["python", "visualize.py"])

    self.send_response(303)
    self.send_header("Location", "/")
    self.end_headers()

if __name__ == "__main__":
    init_db()
