import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for
import calendar
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "my-db")
DB_USER = os.getenv("DB_USER", "guest")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

from datetime import date
import calendar
from flask import request, render_template

@app.get("/")
def index():
    # クエリ（例: /?y=2026&m=1）を受け取る。なければ今月。
    today = date.today()
    y = request.args.get("y", type=int) or today.year
    m = request.args.get("m", type=int) or today.month

    # 範囲外の保険
    if m < 1:
        y -= 1
        m = 12
    if m > 12:
        y += 1
        m = 1

    # 前月・次月
    prev_y, prev_m = (y - 1, 12) if m == 1 else (y, m - 1)
    next_y, next_m = (y + 1, 1) if m == 12 else (y, m + 1)

    # DBから当月の記録を取得
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, entry_date, color_code
                FROM color_entries
                WHERE EXTRACT(YEAR FROM entry_date) = %s
                  AND EXTRACT(MONTH FROM entry_date) = %s
                """,
                (y, m),
            )
            rows = cur.fetchall()

    # 日付(1-31) → 記録 の辞書（同日の複数件は最後の1件を採用）
    entry_map = {r[1].day: {"id": r[0], "color": r[2]} for r in rows}

    # カレンダー配列を作る
    cal = calendar.monthcalendar(y, m)
    calendar_days = []
    for week in cal:
        for d in week:
            if d == 0:
                calendar_days.append({"day": "", "entry": None, "is_today": False})
            else:
                is_today = (y == today.year and m == today.month and d == today.day)
                calendar_days.append(
                    {"day": d, "entry": entry_map.get(d), "is_today": is_today}
                )

    return render_template(
        "index.html",
        calendar_days=calendar_days,
        year=y,
        month=m,
        prev_y=prev_y,
        prev_m=prev_m,
        next_y=next_y,
        next_m=next_m,
    )




@app.get("/new")
def new():
    return render_template("new.html", today=date.today().isoformat())


@app.post("/create")
def create():
    entry_date = request.form.get("entry_date") or date.today().isoformat()
    color_code = request.form.get("color_code") or "#000000"
    memo = request.form.get("memo") or None

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO color_entries (entry_date, color_code, memo) VALUES (%s, %s, %s)",
                (entry_date, color_code, memo),
            )
    return redirect(url_for("index"))


@app.get("/edit/<int:entry_id>")
def edit(entry_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, entry_date, color_code, memo FROM color_entries WHERE id = %s",
                (entry_id,),
            )
            e = cur.fetchone()
    return render_template("edit.html", e=e)


@app.post("/update/<int:entry_id>")
def update(entry_id: int):
    entry_date = request.form["entry_date"]
    color_code = request.form["color_code"]
    memo = request.form.get("memo") or None

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE color_entries
                SET entry_date = %s, color_code = %s, memo = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (entry_date, color_code, memo, entry_id),
            )
    return redirect(url_for("index"))


@app.post("/delete/<int:entry_id>")
def delete(entry_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM color_entries WHERE id = %s", (entry_id,))
    return redirect(url_for("index"))
