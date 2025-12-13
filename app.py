import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    keyword = request.args.get("keyword", "")

    if keyword:
        cur.execute(
            "SELECT * FROM idol WHERE name LIKE ? OR group_name LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        )
    else:
        cur.execute("""
SELECT i.name, i.group_name, p.popularity_score
FROM idol i
LEFT JOIN idol_popularity p
ON i.id = p.idol_id
AND p.year = 2019 AND p.month = 1
""")

    idols = cur.fetchall()

    # 방문객 통계
    cur.execute("SELECT month, visitor_count FROM visit_stats")
    stats_rows = cur.fetchall()

    conn.close()

    monthly_stats = [
        {"month": f"{row['month']}월", "count": row['visitor_count']}
        for row in stats_rows
    ]

    return render_template(
        "index.html",
        idols=idols,
        keyword=keyword,
        monthly_stats=monthly_stats
    )

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/idol/<int:id>")
def idol_detail(id):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 아이돌 기본 정보
    cur.execute("SELECT * FROM idol WHERE id = ?", (id,))
    idol = cur.fetchone()

    # 인기도 정보 (월별)
    cur.execute("""
        SELECT year, month, popularity_score
        FROM idol_popularity
        WHERE idol_id = ?
        ORDER BY year, month
    """, (id,))
    popularity = cur.fetchall()

    conn.close()

    return render_template(
        "idol_detail.html",
        idol=idol,
        popularity=popularity
    )
