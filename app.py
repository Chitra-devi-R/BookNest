import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "data/booknest.db")

BOOKS = [
    {"id": 1, "title": "Pro Git", "author": "Scott Chacon", "category": "DevOps", "copies": 3, "emoji": "🌿"},
    {"id": 2, "title": "The Phoenix Project", "author": "Gene Kim", "category": "DevOps", "copies": 2, "emoji": "🔥"},
    {"id": 3, "title": "Docker Deep Dive", "author": "Nigel Poulton", "category": "DevOps", "copies": 3, "emoji": "🐳"},
    {"id": 4, "title": "Fluent Python", "author": "Luciano Ramalho", "category": "Programming", "copies": 2, "emoji": "🐍"},
    {"id": 5, "title": "Clean Code", "author": "Robert C. Martin", "category": "Programming", "copies": 4, "emoji": "🧼"},
    {"id": 6, "title": "Python for Data Analysis", "author": "Wes McKinney", "category": "Data", "copies": 2, "emoji": "📊"},
    {"id": 7, "title": "Wings of Fire", "author": "A.P.J. Abdul Kalam", "category": "Biography", "copies": 5, "emoji": "🚀"},
    {"id": 8, "title": "The Alchemist", "author": "Paulo Coelho", "category": "Fiction", "copies": 3, "emoji": "✨"},
]


def get_db():
    folder = os.path.dirname(DB_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            book_title TEXT NOT NULL,
            student TEXT NOT NULL,
            reserved_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    conn.close()


init_db()


def books_with_availability():
    conn = get_db()
    counts = {
        r["book_id"]: r["n"]
        for r in conn.execute("SELECT book_id, COUNT(*) AS n FROM reservations GROUP BY book_id")
    }
    conn.close()
    return [dict(b, available=b["copies"] - counts.get(b["id"], 0)) for b in BOOKS]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/books")
def api_books():
    return jsonify(books_with_availability())


@app.route("/api/reserve", methods=["POST"])
def reserve():
    data = request.get_json(silent=True) or {}
    student = (data.get("student") or "").strip()
    book_id = data.get("book_id")
    if not student:
        return jsonify(success=False, message="Student name is required"), 400
    book = next((b for b in books_with_availability() if b["id"] == book_id), None)
    if not book:
        return jsonify(success=False, message="Book not found"), 404
    if book["available"] <= 0:
        return jsonify(success=False, message="No copies available"), 409
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO reservations (book_id, book_title, student) VALUES (?, ?, ?)",
        (book["id"], book["title"], student),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return jsonify(success=True, reservation_id=rid, title=book["title"])


@app.route("/reservations")
def reservations():
    conn = get_db()
    rows = conn.execute("SELECT * FROM reservations ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("reservations.html", rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
