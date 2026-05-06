from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.tables import Table
from flask import send_file

app = Flask(__name__)
CORS(app)

# Absolute database path
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "expenses.db"

# Database connection
def connect():
    return sqlite3.connect(str(DATABASE))

# Initialize database
def init_db():

    conn = connect()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# Home route
@app.route("/")
def home():
    return jsonify({
        "message": "Smart Expense Tracker API Running"
    })

# Signup route
@app.route("/signup", methods=["POST"])
def signup():

    data = request.json

    username = data["username"]
    password = data["password"]

    conn = connect()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, password))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Signup successful"
        })

    except:

        return jsonify({
            "success": False,
            "message": "Username already exists"
        })

    finally:
        conn.close()

# Login route
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data["username"]
    password = data["password"]

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()

    if user:

        return jsonify({
            "success": True,
            "user_id": user[0],
            "message": "Login successful"
        })

    else:

        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        })

# Add expense
@app.route("/add", methods=["POST"])
def add_expense():

    data = request.json

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
       INSERT INTO expenses (user_id, title, amount, category, date)
VALUES (?, ?, ?, ?, ?)
    """, (
        data["user_id"],
        data["title"],
        data["amount"],
        data["category"],
        data["date"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Expense added successfully"
    })

# Get all expenses
@app.route("/expenses/<int:user_id>", methods=["GET"])
def get_expenses(user_id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    expenses = []

    for row in rows:
        expenses.append({
            "id": row[0],
            "title": row[2],
            "amount": row[3],
            "category": row[4],
            "date": row[5]
        })

    return jsonify(expenses)

# Delete expense
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_expense(id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Expense deleted successfully"
    })

# Total spending
@app.route("/total", methods=["GET"])
def total_spending():

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return jsonify({
        "total_spending": total
    })
@app.route("/report/<int:user_id>")
def generate_report(user_id):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, amount, category, date
        FROM expenses
        WHERE user_id=?
    """, (user_id,))

    expenses = cursor.fetchall()

    conn.close()

    pdf_path = "expense_report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "SmartSpend AI - Expense Report",
        styles['Title']
    )

    elements.append(title)

    elements.append(Spacer(1, 20))

    data = [["Title", "Amount", "Category", "Date"]]

    total = 0

    for expense in expenses:

        data.append([
            expense[0],
            str(expense[1]),
            expense[2],
            expense[3]
        ])

        total += expense[1]

    data.append([
        "",
        f"Total = ₹{total}",
        "",
        ""
    ])

    table = Table(data)

    elements.append(table)

    doc.build(elements)

    return send_file(
        pdf_path,
        as_attachment=True
    )
if __name__ == "__main__":
    app.run(debug=True)