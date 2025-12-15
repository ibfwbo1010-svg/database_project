import sqlite3
from flask import Flask, render_template, request
print("=== THIS IS MY APP.PY ===")

app = Flask(__name__)

# 메인 페이지: 월별 TOP 5 아이돌
@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    month = request.args.get("month", "1")

    cur.execute("""
        SELECT
            i.id,
            i.name,
            i.group_name,
            i.image,
            p.popularity_score
        FROM idol i
        JOIN idol_popularity p
        ON i.id = p.idol_id
        WHERE p.year = 2019
          AND p.month = ?
        ORDER BY p.popularity_score DESC
        LIMIT 5
    """, (month,))
    top_idols = cur.fetchall()

    conn.close()

    return render_template(
        "index.html",
        top_idols=top_idols,
        selected_month=month
    )


# 아이돌 상세 페이지
@app.route("/idol/<int:id>")
def idol_detail(id):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM idol WHERE id = ?", (id,))
    idol = cur.fetchone()

    cur.execute("""
        SELECT year, month, popularity_score
        FROM idol_popularity
        WHERE idol_id = ?
        ORDER BY month
    """, (id,))
    popularity = cur.fetchall()

    cur.execute("""
        SELECT
            AVG(popularity_score) AS avg_score,
            MAX(popularity_score) AS max_score
        FROM idol_popularity
        WHERE idol_id = ?
    """, (id,))
    stats = cur.fetchone()

    cur.execute("""
        SELECT year, month
        FROM idol_popularity
        WHERE idol_id = ?
        ORDER BY popularity_score DESC
        LIMIT 1
    """, (id,))
    peak = cur.fetchone()

    conn.close()

    return render_template(
        "idol_detail.html",
        idol=idol,
        popularity=popularity,
        stats=stats,
        peak=peak
    )


# 그룹별 소개 페이지 
@app.route("/groups")
def groups():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT group_name, name, image, id
        FROM idol
        ORDER BY group_name, name
    """)
    rows = cur.fetchall()
    conn.close()

    grouped = {}
    for row in rows:
        group = row["group_name"]
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(row)

    return render_template("groups.html", groups=grouped)


if __name__ == "__main__":
    app.run(debug=True)
