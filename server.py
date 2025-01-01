from http.server import SimpleHTTPRequestHandler, HTTPServer
import sqlite3
import urllib.parse
import os
import csv

DB_FILE = "finance.db"
PORT = 8000


class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.show_homepage()
        elif self.path == "/summary":
            self.show_summary()
        elif self.path.startswith("/edit-expense"):
            self.show_edit_page()
        elif self.path.startswith("/delete-expense"):
            self.confirm_delete()
        elif self.path == "/export-expenses":
            self.export_to_csv()
        else:
            self.send_error(404, "Page not found.")

    def do_POST(self):
        if self.path.startswith("/add-expense"):
            self.add_expense()
        elif self.path.startswith("/edit-expense"):
            self.update_expense()
        elif self.path.startswith("/delete-expense"):
            self.delete_expense()

    def add_expense(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)
        category = data.get('category', [''])[0]
        record_type = data.get('type', [''])[0]
        amount = float(data.get('amount', ['0'])[0])
        date = data.get('date', [''])[0]

        if category and record_type and amount and date:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO records (category, type, amount, date) VALUES (?, ?, ?, ?)",
                           (category, record_type, amount, date))
            conn.commit()
            conn.close()

            self.send_response(303)
            self.send_header("Location", "/summary")
            self.end_headers()
        else:
            self.send_error(400, "Missing or incorrect data.")

    def export_to_csv(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, category, amount, date FROM records WHERE type = 'expense'")
        expenses = cursor.fetchall()
        with open("expenses.csv", "w", newline="") as expense_file:
            expense_writer = csv.writer(expense_file)
            expense_writer.writerow(["ID", "Category", "Amount", "Date"])
            expense_writer.writerows(expenses)

        cursor.execute("SELECT id, category, amount, date FROM records WHERE type = 'income'")
        incomes = cursor.fetchall()
        with open("income.csv", "w", newline="") as income_file:
            income_writer = csv.writer(income_file)
            income_writer.writerow(["ID", "Category", "Amount", "Date"])
            income_writer.writerows(incomes)

        conn.close()

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Export Success</title>
        </head>
        <body>
            <h1>Export Successful</h1>
            <p>Records have been successfully exported to <strong>expenses.csv</strong> and <strong>income.csv</strong>.</p>
            <a href="/">Go Back</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def show_homepage(self):
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Financial Tracker</title>
        </head>
        <body>
            <h1>Financial Tracker</h1>
            <h2>Add Transaction</h2>
            <form action="/add-expense" method="post">
                <label>Category: </label>
                <input type="text" name="category" required><br>
                <label>Type: </label>
                <select name="type" required>
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                </select><br>
                <label>Amount: </label>
                <input type="number" step="0.01" name="amount" required><br>
                <label>Date: </label>
                <input type="date" name="date" required><br>
                <button type="submit">Add Transaction</button>
            </form>
            <br>
            <a href="/summary">View Summary</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def show_summary(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, type, amount, date FROM records")
        records = cursor.fetchall()
        conn.close()

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Summary</title>
        </head>
        <body>
            <h1>Summary</h1>
            <table border="1">
                <tr><th>Category</th><th>Type</th><th>Amount</th><th>Date</th><th>Actions</th></tr>
        """
        for row in records:
            html += f"<tr><td>{row[1]}</td><td>{row[2].capitalize()}</td><td>{row[3]:.2f}</td><td>{row[4]}</td>"
            html += f"<td><a href='/edit-expense?id={row[0]}'>Edit</a> | <a href='/delete-expense?id={row[0]}'>Delete</a></td></tr>"
        html += """
            </table>
            <br>
            <a href="/">Go Back</a>
            <br>
            <a href="/export-expenses">Export to CSV</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def show_edit_page(self):
        query = urllib.parse.urlparse(self.path).query
        record_id = urllib.parse.parse_qs(query).get("id", [None])[0]

        if not record_id:
            self.send_error(400, "Record ID is missing.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT category, type, amount, date FROM records WHERE id = ?", (record_id,))
        record = cursor.fetchone()
        conn.close()

        if not record:
            self.send_error(404, "Record not found.")
            return

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Edit Expense</title>
        </head>
        <body>
            <h1>Edit Expense</h1>
            <form action="/edit-expense?id={record_id}" method="post">
                <label>Category: </label>
                <input type="text" name="category" value="{record[0]}" required><br>
                <label>Type: </label>
                <select name="type" required>
                    <option value="expense" {"selected" if record[1] == "expense" else ""}>Expense</option>
                    <option value="income" {"selected" if record[1] == "income" else ""}>Income</option>
                </select><br>
                <label>Amount: </label>
                <input type="number" step="0.01" name="amount" value="{record[2]}" required><br>
                <label>Date: </label>
                <input type="date" name="date" value="{record[3]}" required><br>
                <button type="submit">Update</button>
            </form>
            <br>
            <a href="/summary">Cancel</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def update_expense(self):
        query = urllib.parse.urlparse(self.path).query
        record_id = urllib.parse.parse_qs(query).get("id", [None])[0]

        if not record_id:
            self.send_error(400, "Record ID is missing.")
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)
        category = data.get('category', [''])[0]
        record_type = data.get('type', [''])[0]
        amount = float(data.get('amount', ['0'])[0])
        date = data.get('date', [''])[0]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE records SET category = ?, type = ?, amount = ?, date = ? WHERE id = ?",
                       (category, record_type, amount, date, record_id))
        conn.commit()
        conn.close()

        self.send_response(303)
        self.send_header("Location", "/summary")
        self.end_headers()

    def confirm_delete(self):
        query = urllib.parse.urlparse(self.path).query
        record_id = urllib.parse.parse_qs(query).get("id", [None])[0]

        if not record_id:
            self.send_error(400, "Record ID is missing.")
            return

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Confirm Delete</title>
        </head>
        <body>
            <h1>Confirm Delete</h1>
            <p>Are you sure you want to delete this record?</p>
            <form action="/delete-expense?id={record_id}" method="post">
                <button type="submit">Yes, Delete</button>
            </form>
            <br>
            <a href="/summary">Cancel</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def delete_expense(self):
        query = urllib.parse.urlparse(self.path).query
        record_id = urllib.parse.parse_qs(query).get("id", [None])[0]

        if not record_id:
            self.send_error(400, "Record ID is missing.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()

        self.send_response(303)
        self.send_header("Location", "/summary")
        self.end_headers()


if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
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

    server = HTTPServer(("localhost", PORT), RequestHandler)
    print(f"Server running on http://localhost:{PORT}")
    server.serve_forever()
