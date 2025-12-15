import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    month = request.args.get("month", "1")

    conn = get_db()
    cur = conn.cursor()

    # =========================
    # 1. 베트남 관광객 수 (없어도 안 깨지게)
    # =========================
    visitor = None
    try:
        cur.execute("""
            SELECT visitor_count
            FROM vietnam_visitors
            WHERE year = 2019 AND month = ?
        """, (month,))
        visitor = cur.fetchone()
    except sqlite3.OperationalError:
        visitor = None

    # =========================
    # 2. 월별 TOP 키워드
    # =========================
    top_keywords = []
    try:
        cur.execute("""
            SELECT keyword, SUM(keyword_count) AS total_count
            FROM keyword_trend
            WHERE year = 2019 AND month = ?
            GROUP BY keyword
            ORDER BY total_count DESC
            LIMIT 10
        """, (month,))
        top_keywords = cur.fetchall()
    except sqlite3.OperationalError:
        top_keywords = []

    # =========================
    # 3. 커뮤니티 반영 TOP 5 아이돌
    # =========================
    top_idols = []
    try:
        cur.execute("""
            SELECT
                i.id,
                i.name,
                i.group_name,
                i.image,
                p.popularity_score +
                IFNULL(SUM(k.keyword_count) * 0.01, 0) AS adjusted_score
            FROM idol i
            JOIN idol_popularity p
              ON i.id = p.idol_id
            LEFT JOIN keyword_trend k
              ON (
                  LOWER(k.keyword) LIKE '%' || LOWER(i.name) || '%'
                  OR LOWER(k.keyword) LIKE '%' || LOWER(i.group_name) || '%'
              )
              AND k.year = 2019 AND k.month = ?
            WHERE p.year = 2019 AND p.month = ?
            GROUP BY i.id
            ORDER BY adjusted_score DESC
            LIMIT 5
        """, (month, month))
        top_idols = cur.fetchall()
    except sqlite3.OperationalError:
        top_idols = []

    # =========================
    # 4. 자동 설명 문장 (1위 기준)
    # =========================
    explanation = None
    if top_idols:
        top = top_idols[0]
        explanation = (
            f"{month}월 베트남 커뮤니티에서는 "
            f"'{top['name']}' 및 '{top['group_name']}' 관련 키워드 언급량이 증가하며 "
            f"커뮤니티 관심도가 반영되어 1위를 차지했습니다."
        )

    # =========================
    # 5. 게시글 (없어도 안 깨지게)
    # =========================
    posts = []
    try:
        cur.execute("SELECT * FROM post ORDER BY id DESC")
        posts = cur.fetchall()
    except sqlite3.OperationalError:
        posts = []

    conn.close()

    return render_template(
        "index.html",
        selected_month=month,
        visitor=visitor,
        top_keywords=top_keywords,
        top_idols=top_idols,
        explanation=explanation,
        posts=posts
    )


# =========================
# 아이돌 상세 페이지 (안정 버전)
# =========================
@app.route("/idol/<int:id>")
def idol_detail(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM idol WHERE id = ?", (id,))
    idol = cur.fetchone()

    if idol is None:
        conn.close()
        return "아이돌 정보를 찾을 수 없습니다.", 404

    popularity = []
    try:
        cur.execute("""
            SELECT month, popularity_score
            FROM idol_popularity
            WHERE idol_id = ? AND year = 2019
            ORDER BY month
        """, (id,))
        popularity = cur.fetchall()
    except sqlite3.OperationalError:
        popularity = []

    keywords = []
    try:
        cur.execute("""
            SELECT keyword, SUM(keyword_count) AS total_count
            FROM keyword_trend
            WHERE year = 2019
              AND (
                  LOWER(keyword) LIKE '%' || LOWER(?) || '%'
                  OR LOWER(keyword) LIKE '%' || LOWER(?) || '%'
              )
            GROUP BY keyword
            ORDER BY total_count DESC
            LIMIT 5
        """, (idol["name"], idol["group_name"]))
        keywords = cur.fetchall()
    except sqlite3.OperationalError:
        keywords = []

    conn.close()

    return render_template(
        "idol_detail.html",
        idol=idol,
        popularity=popularity,
        keywords=keywords
    )


# =========================
# 게시글 / 댓글 (있으면 쓰고, 없어도 서버 안 죽음)
# =========================
@app.route("/post", methods=["POST"])
def add_post():
    try:
        title = request.form["title"]
        content = request.form["content"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO post (title, content, created_at)
            VALUES (?, ?, ?)
        """, (title, content, datetime.now()))
        conn.commit()
        conn.close()
    except Exception:
        pass

    return redirect(url_for("home"))


@app.route("/comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    try:
        content = request.form["content"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO comment (post_id, content, created_at)
            VALUES (?, ?, ?)
        """, (post_id, content, datetime.now()))
        conn.commit()
        conn.close()
    except Exception:
        pass

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
