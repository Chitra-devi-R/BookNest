
import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "data/booknest.db")

DEFAULT_BOOKS = [
    (1, "Pro Git", "Scott Chacon", "DevOps", 3, "🌿"),
    (2, "The Phoenix Project", "Gene Kim", "DevOps", 2, "🔥"),
    (3, "Docker Deep Dive", "Nigel Poulton", "DevOps", 3, "🐳"),
    (4, "Fluent Python", "Luciano Ramalho", "Programming", 2, "🐍"),
    (5, "Clean Code", "Robert C. Martin", "Programming", 4, "🧼"),
    (6, "Python for Data Analysis", "Wes McKinney", "Data", 2, "📊"),
    (7, "Wings of Fire", "A.P.J. Abdul Kalam", "Biography", 5, "🚀"),
    (8, "The Alchemist", "Paulo Coelho", "Fiction", 3, "✨"),
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            copies INTEGER NOT NULL DEFAULT 1,
            emoji TEXT DEFAULT '📚'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            book_title TEXT NOT NULL,
            student TEXT NOT NULL,
            reserved_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)",
            DEFAULT_BOOKS
        )
    conn.commit()
    conn.close()


init_db()


def get_books():
    conn = get_db()
    rows = conn.execute("""
        SELECT b.*,
        b.copies - (
            SELECT COUNT(*) FROM reservations r
            WHERE r.book_id = b.id
        ) AS available
        FROM books b ORDER BY b.id
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def error(message, status=400):
    return jsonify(success=False, message=message), status


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/books")
def api_books():
    return jsonify(get_books())


@app.route("/api/books/<int:book_id>")
def book_details(book_id):
    book = next((b for b in get_books() if b["id"] == book_id), None)
    if not book:
        return error("Book not found", 404)
    return jsonify(book)


@app.route("/api/reserve", methods=["POST"])
def reserve():
    data = request.get_json(silent=True) or {}
    student = str(data.get("student") or "").strip()

    try:
        book_id = int(data.get("book_id"))
    except (TypeError, ValueError):
        return error("Invalid book ID")

    if not student:
        return error("Student name is required")

    conn = get_db()
    book = conn.execute(
        "SELECT * FROM books WHERE id = ?", (book_id,)
    ).fetchone()

    if not book:
        conn.close()
        return error("Book not found", 404)

    reserved = conn.execute(
        "SELECT COUNT(*) FROM reservations WHERE book_id = ?",
        (book_id,)
    ).fetchone()[0]

    if reserved >= book["copies"]:
        conn.close()
        return error("No copies available", 409)

    cur = conn.execute(
        "INSERT INTO reservations (book_id, book_title, student) "
        "VALUES (?, ?, ?)",
        (book_id, book["title"], student)
    )
    conn.commit()
    reservation_id = cur.lastrowid
    conn.close()

    return jsonify(success=True, reservation_id=reservation_id,
                   title=book["title"])


@app.route("/reservations")
def reservations():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM reservations ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("reservations.html", rows=rows)


@app.route("/api/reservations")
def api_reservations():
    student = request.args.get("student", "").strip()
    conn = get_db()

    if student:
        rows = conn.execute(
            "SELECT * FROM reservations WHERE student = ? ORDER BY id DESC",
            (student,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM reservations ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/reservations/<int:reservation_id>", methods=["DELETE"])
def cancel_reservation(reservation_id):
    conn = get_db()
    cur = conn.execute(
        "DELETE FROM reservations WHERE id = ?", (reservation_id,)
    )
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return error("Reservation not found", 404)
    return jsonify(success=True, message="Reservation cancelled")


@app.route("/admin")
def admin():
    return render_template("admin.html", books=get_books())


@app.route("/api/admin/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title") or "").strip()
    author = str(data.get("author") or "").strip()
    category = str(data.get("category") or "").strip()

    try:
        copies = int(data.get("copies", 1))
    except (TypeError, ValueError):
        return error("Copies must be a number")

    if not title or not author or not category:
        return error("Title, author and category are required")
    if copies < 1:
        return error("Copies must be at least 1")

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO books (title, author, category, copies, emoji) "
        "VALUES (?, ?, ?, ?, ?)",
        (title, author, category, copies,
         str(data.get("emoji") or "📚"))
    )
    conn.commit()
    book_id = cur.lastrowid
    conn.close()

    return jsonify(success=True, id=book_id), 201


@app.route("/api/admin/books/<int:book_id>", methods=["PUT"])
def edit_book(book_id):
    data = request.get_json(silent=True) or {}
    title = str(data.get("title") or "").strip()
    author = str(data.get("author") or "").strip()
    category = str(data.get("category") or "").strip()

    try:
        copies = int(data.get("copies", 1))
    except (TypeError, ValueError):
        return error("Copies must be a number")

    if not title or not author or not category or copies < 1:
        return error("Enter valid book details and copies")

    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM books WHERE id = ?", (book_id,)
    ).fetchone()
    if not existing:
        conn.close()
        return error("Book not found", 404)

    reserved = conn.execute(
        "SELECT COUNT(*) FROM reservations WHERE book_id = ?",
        (book_id,)
    ).fetchone()[0]
    if copies < reserved:
        conn.close()
        return error("Copies cannot be fewer than active reservations")

    conn.execute(
        "UPDATE books SET title=?, author=?, category=?, copies=?, emoji=? "
        "WHERE id=?",
        (title, author, category, copies,
         str(data.get("emoji") or existing["emoji"]), book_id)
    )
    conn.commit()
    conn.close()
    return jsonify(success=True)


@app.route("/api/admin/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    conn = get_db()
    reserved = conn.execute(
        "SELECT COUNT(*) FROM reservations WHERE book_id = ?",
        (book_id,)
    ).fetchone()[0]

    if reserved:
        conn.close()
        return error("Cancel active reservations before deleting this book", 409)

    cur = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return error("Book not found", 404)
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
