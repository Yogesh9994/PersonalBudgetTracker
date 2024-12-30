from http.server import SimpleHTTPRequestHandler, HTTPServer
import sqlite3
import urllib.parse
import os

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
            self.delete_expense()
        else:
            self.send_error(404, "Page not found.")

    def do_POST(self):

        if self.path.startswith("/add-expense"):
            self.add_expense()
        elif self.path.startswith("/edit-expense"):
            self.update_expense()

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
            <form action="/add-expense" method="post">
                <label>Category: </label>
                <input type="text" name="category" required><br>
                <label>Amount: </label>
                <input type="number" step="0.01" name="amount" required><br>
                <label>Date: </label>
                <input type="date" name="date" required><br>
                <button type="submit">Add Expense</button>
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

    def add_expense(self):

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(post_data)

        category = data['category'][0]
        amount = float(data['amount'][0])
        date = data['date'][0]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
                       (category, amount, date))
        conn.commit()
        conn.close()

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def show_summary(self):

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, amount, date FROM expenses")
        expenses = cursor.fetchall()
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
                <tr><th>Category</th><th>Amount</th><th>Date</th><th>Actions</th></tr>
        """
        for row in expenses:
            html += f"<tr><td>{row[1]}</td><td>{row[2]:.2f}</td><td>{row[3]}</td>"
            html += f"<td><a href='/edit-expense?id={row[0]}'>Edit</a> | <a href='/delete-expense?id={row[0]}'>Delete</a></td></tr>"
        html += """
            </table>
            <br>
            <a href="/">Go Back</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def show_edit_page(self):

        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'id' not in query_params:
            self.send_error(400, "Missing expense ID.")
            return

        expense_id = query_params['id'][0]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT category, amount, date FROM expenses WHERE id=?", (expense_id,))
        expense = cursor.fetchone()
        conn.close()

        if not expense:
            self.send_error(404, "Expense not found.")
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
            <form action="/edit-expense?id={expense_id}" method="post">
                <label>Category: </label>
                <input type="text" name="category" value="{expense[0]}" required><br>
                <label>Amount: </label>
                <input type="number" step="0.01" name="amount" value="{expense[1]}" required><br>
                <label>Date: </label>
                <input type="date" name="date" value="{expense[2]}" required><br>
                <button type="submit">Update Expense</button>
            </form>
            <br>
            <a href="/summary">Go Back</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def update_expense(self):

        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'id' not in query_params:
            self.send_error(400, "Missing expense ID.")
            return

        expense_id = query_params['id'][0]

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(post_data)

        category = data['category'][0]
        amount = float(data['amount'][0])
        date = data['date'][0]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE expenses SET category=?, amount=?, date=? WHERE id=?",
                       (category, amount, date, expense_id))
        conn.commit()
        conn.close()

        self.send_response(303)
        self.send_header("Location", "/summary")
        self.end_headers()

    def delete_expense(self):

        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'id' not in query_params:
            self.send_error(400, "Missing expense ID.")
            return

        expense_id = query_params['id'][0]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
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
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount REAL,
                date TEXT
            )
        """)
        conn.commit()
        conn.close()

    server = HTTPServer(("localhost", PORT), RequestHandler)
    print(f"Server running on http://localhost:{PORT}")
    server.serve_forever()
