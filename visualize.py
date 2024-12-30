import sqlite3
import matplotlib.pyplot as plt

DB_FILE = "finance.db"

def fetch_data_from_db():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()

    conn.close()

    categories = [row[0] for row in rows]
    amounts = [row[1] for row in rows]

    return categories, amounts

def generate_pie_chart(categories, amounts):

    plt.figure(figsize=(7, 7))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)

    plt.title("Expense Distribution")

    plt.show()

def update_pie_chart():

    categories, amounts = fetch_data_from_db()

    generate_pie_chart(categories, amounts)

if __name__ == "__main__":

    update_pie_chart()
