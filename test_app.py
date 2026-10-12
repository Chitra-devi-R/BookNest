import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

import app as booknest  # noqa: E402


def client():
    booknest.app.config["TESTING"] = True
    return booknest.app.test_client()


def test_health():
    r = client().get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_books_listed():
    r = client().get("/api/books")
    assert r.status_code == 200
    assert len(r.get_json()) == 8


def test_reserve_book():
    c = client()
    r = c.post("/api/reserve", json={"student": "Jayasree", "book_id": 1})
    assert r.status_code == 200
    assert r.get_json()["success"] is True


def test_reserve_requires_name():
    r = client().post("/api/reserve", json={"student": "", "book_id": 1})
    assert r.status_code == 400
