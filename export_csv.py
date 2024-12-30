import sqlite3
import csv

def export_to_csv():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    with open("expenses.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Category", "Amount", "Date"])
        writer.writerows(rows)

    print("Data exported to expenses.csv")

if __name__ == "__main__":
    export_to_csv()
