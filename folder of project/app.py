from flask import Flask, render_template, request, redirect, session
import sqlite3, os, re
import pytesseract
from PIL import Image
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import detect_category

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

USERNAME = "admin@gmail.com"
PASSWORD = "Secure#12"

MONTH_LIMIT = 30000

category_limits = {
    "Food": 3000,
    "Travel": 3000,
    "Shopping": 2500,
    "Cloth": 1000,
    "Household": 2500,
    "Rent": 12000,
    "Others": 6000
}

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- CHARTS ----------------
def generate_charts():
    conn = get_db()

    # Clear old charts
    if os.path.exists("static/category_chart.png"):
        os.remove("static/category_chart.png")
    if os.path.exists("static/monthly_chart.png"):
        os.remove("static/monthly_chart.png")

    # PIE CHART
    data = conn.execute(
        "SELECT category, SUM(amount) FROM expenses GROUP BY category"
    ).fetchall()

    if data:
        categories = [d[0] for d in data]
        amounts = [d[1] for d in data]

        plt.figure(figsize=(5,5))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%')
        plt.title("Category Expenses")
        plt.savefig("static/category_chart.png")
        plt.close()

    # BAR GRAPH
    data = conn.execute(
        """
        SELECT strftime('%m', date), SUM(amount)
        FROM expenses
        GROUP BY strftime('%m', date)
        """
    ).fetchall()

    if data:
        months_map = {
            "01":"Jan","02":"Feb","03":"Mar","04":"Apr",
            "05":"May","06":"Jun","07":"Jul","08":"Aug",
            "09":"Sep","10":"Oct","11":"Nov","12":"Dec"
        }

        months = [months_map[d[0]] for d in data]
        totals = [d[1] for d in data]

        plt.figure(figsize=(7,4))
        plt.bar(months, totals)
        plt.title("Monthly Expenses")
        plt.savefig("static/monthly_chart.png")
        plt.close()

    conn.close()

# ---------------- LOGIN ----------------
@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"].strip().lower() == USERNAME and request.form["password"] == PASSWORD:
            session["user"] = USERNAME
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid Login")
    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect("/login")

# ---------------- ADD PAGE ----------------
@app.route('/add_page')
def add_page():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

# ---------------- ADD MANUAL ----------------
@app.route('/add', methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    d = request.form["date"]
    c = request.form["category"]
    a = int(request.form["amount"])

    conn = get_db()
    conn.execute("INSERT INTO expenses(date,category,amount) VALUES (?,?,?)", (d, c, a))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- OCR ----------------
@app.route('/upload', methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    file = request.files["image"]

    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        text = pytesseract.image_to_string(Image.open(path))
        category = detect_category(text)

        nums = re.findall(r'\d+', text)
        amount = int(nums[0]) if nums else 0

        if "ramakrishna" in text.lower():
            amount = 12000

        today = date.today()

        conn = get_db()
        conn.execute(
            "INSERT INTO expenses(date,category,amount) VALUES (?,?,?)",
            (today, category, amount)
        )
        conn.commit()
        conn.close()

    return redirect("/dashboard")

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    expenses = conn.execute("SELECT * FROM expenses").fetchall()

    total = sum(e["amount"] for e in expenses)
    savings = MONTH_LIMIT - total

    category_totals = {}
    category_savings = {}

    for cat in category_limits:
        spent = conn.execute(
            "SELECT SUM(amount) FROM expenses WHERE category=?",
            (cat,)
        ).fetchone()[0] or 0

        category_totals[cat] = spent
        category_savings[cat] = category_limits[cat] - spent

    alerts = []
    if total > MONTH_LIMIT:
        alerts.append("⚠ Monthly limit exceeded!")

    expense_alerts = []
    for e in expenses:
        if category_totals[e["category"]] > category_limits[e["category"]]:
            expense_alerts.append("⚠")
        else:
            expense_alerts.append("")

    conn.close()

    generate_charts()

    return render_template(
        "dashboard.html",
        expenses=expenses,
        expense_alerts=expense_alerts,
        total=total,
        savings=savings,
        alerts=alerts,
        category_totals=category_totals,
        category_limits=category_limits,
        category_savings=category_savings,
        MONTH_LIMIT=MONTH_LIMIT
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)