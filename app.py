import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT month, visitor_count FROM visit_stats")
    rows = cur.fetchall()

    conn.close()

    monthly_stats = [
        {"month": f"{row[0]}월", "count": row[1]}
        for row in rows
    ]

    return render_template("index.html", monthly_stats=monthly_stats)

if __name__ == "__main__":
    app.run(debug=True)
