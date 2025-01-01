import sqlite3
import matplotlib.pyplot as plt

DB_FILE = "finance.db"

def fetch_data(record_type):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT category, SUM(amount) FROM records WHERE type=? GROUP BY category", (record_type,))
    rows = cursor.fetchall()

    conn.close()
    return rows

def generate_pie_chart(data, record_type):
    """
    """
    if not data:
        print(f"No {record_type} data found.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(8, 8))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title(f"{record_type.capitalize()} Distribution by Category")
    plt.axis('equal')

    plt.show()

def main():
    """
    """
    while True:
        record_type = input("Enter the type of transaction to visualize (expense/income): ").strip().lower()
        if record_type in ("expense", "income"):
            break
        print("Invalid input. Please enter 'expense' or 'income'.")

    data = fetch_data(record_type)
    generate_pie_chart(data, record_type)

if __name__ == "__main__":
    main()
