import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# =========================
# DB 연결 헬퍼
# =========================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# 메인 페이지
# - 전체 아이돌 목록 표시
# - 월 선택 가능
# - 베트남 방문객 수
# - 월별 TOP 키워드
# =========================
@app.route("/")
def home():
    month = request.args.get("month", "1")

    conn = get_db()
    cur = conn.cursor()

    # -------------------------
    # 1. 베트남 관광객 수
    # -------------------------
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

    # -------------------------
    # 2. 월별 TOP 키워드
    # -------------------------
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

    # -------------------------
    # 3. 전체 아이돌 목록 (메인 페이지용)
    # -------------------------
    cur.execute("""
        SELECT id, name, group_name, image
        FROM idol
        ORDER BY name
    """)
    idols = cur.fetchall()

    # -------------------------
    # 4. 게시글 목록 (최대 10개)
    # -------------------------
    posts = []
    try:
        cur.execute("""
            SELECT *
            FROM post
            ORDER BY id DESC
            LIMIT 10
        """)
        posts = cur.fetchall()
    except sqlite3.OperationalError:
        posts = []

    conn.close()

    return render_template(
        "index.html",
        selected_month=month,
        visitor=visitor,
        top_keywords=top_keywords,
        idols=idols,
        posts=posts
    )


# =========================
# 아이돌 개인 페이지
# - 기본 정보
# - 월별 인기도 테이블
# - 커뮤니티 주요 키워드
# =========================
@app.route("/idol/<int:id>")
def idol_detail(id):
    print("DEBUG idol_id:", id)
    conn = get_db()
    cur = conn.cursor()

    # 아이돌 기본 정보
    cur.execute("SELECT * FROM idol WHERE id = ?", (id,))
    idol = cur.fetchone()

    if idol is None:
        conn.close()
        return "아이돌 정보를 찾을 수 없습니다.", 404

    # -------------------------
    # 월별 인기도 (2019)
    # ⚠️ score 컬럼 기준
    # -------------------------
    popularity = []
    try:
        cur.execute("""
            SELECT
                month,
                popularity_score
            FROM idol_popularity
            WHERE idol_id = ?
              AND year = 2019
            ORDER BY month
        """, (id,))
        popularity = cur.fetchall()
    except sqlite3.OperationalError:
        popularity = []

    # -------------------------
    # 베트남 커뮤니티 주요 키워드
    # -------------------------
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
# 게시글 작성
# =========================
@app.route("/post", methods=["POST"])
def add_post():
    title = request.form.get("title")
    content = request.form.get("content")

    if not title or not content:
        return redirect(url_for("home"))

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO post (title, content, created_at)
            VALUES (?, ?, ?)
        """, (title, content, datetime.now()))
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()
    return redirect(url_for("home"))


# =========================
# 댓글 작성
# =========================
@app.route("/comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    content = request.form.get("content")

    if not content:
        return redirect(url_for("home"))

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO comment (post_id, content, created_at)
            VALUES (?, ?, ?)
        """, (post_id, content, datetime.now()))
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()
    return redirect(url_for("home"))


# =========================
# 실행
# =========================
if __name__ == "__main__":
    app.run(debug=True)
