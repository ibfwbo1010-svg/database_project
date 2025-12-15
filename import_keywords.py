import csv
import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

with open("KC_KEYWORD_COMMUNITY_IDOL_VN_2019.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        colct = row["COLCT_DE"].strip()

        # 형식 1: Jan-19
        if "-" in colct and colct[:3].isalpha():
            m, y = colct.split("-")
            year = 2000 + int(y)
            month = month_map[m]

        # 형식 2: 2019-01
        elif "-" in colct and colct[:4].isdigit():
            y, m = colct.split("-")
            year = int(y)
            month = int(m)

        else:
            continue

        # ❗ 2019년 데이터만 사용
        if year != 2019:
            continue

        artist = row["ARTS_NM"]
        keyword = row["Community_KEY_W"]
        count = int(row["KWRD_FQ_CO"])

        cur.execute("""
            INSERT INTO keyword_trend
            (year, month, artist, keyword, keyword_count)
            VALUES (?, ?, ?, ?, ?)
        """, (year, month, artist, keyword, count))

conn.commit()
conn.close()

