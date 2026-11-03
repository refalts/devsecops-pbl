"""Aplikasi contoh untuk demonstrasi pipeline DevSecOps (PBL RKS532).

Menerapkan secure coding: parameterized query, validasi input,
password hashing, security headers, dan secret dari environment variable.
"""
import os
import sqlite3

from flask import Flask, jsonify, request, g
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = os.environ.get("DB_PATH", "app.db")

app = Flask(__name__)
# Secret TIDAK di-hardcode: diambil dari environment (dicek Gitleaks di pipeline)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32).hex())


def get_db():
    """Ambil koneksi database per-request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    """Tutup koneksi database setelah request selesai."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Buat tabel users bila belum ada."""
    db = get_db()
    db.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "username TEXT UNIQUE NOT NULL, "
        "password_hash TEXT NOT NULL)"
    )
    db.commit()


@app.after_request
def security_headers(resp):
    """Tambahkan security headers (mitigasi XSS, clickjacking, MIME sniffing)."""
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Cache-Control"] = "no-store"
    return resp


def valid_username(name):
    """Validasi input username (allow-list)."""
    return isinstance(name, str) and 3 <= len(name) <= 30 and name.isalnum()


@app.get("/health")
def health():
    """Endpoint health check untuk DAST & monitoring."""
    return jsonify(status="ok")


@app.post("/register")
def register():
    """Registrasi user dengan password di-hash."""
    data = request.get_json(silent=True) or {}
    username, password = data.get("username"), data.get("password")
    if not valid_username(username) or not isinstance(password, str) or len(password) < 8:
        return jsonify(error="input tidak valid"), 400
    init_db()
    try:
        get_db().execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",  # parameterized
            (username, generate_password_hash(password)),
        )
        get_db().commit()
    except sqlite3.IntegrityError:
        return jsonify(error="username sudah dipakai"), 409
    return jsonify(message="registrasi berhasil"), 201


@app.post("/login")
def login():
    """Login aman: parameterized query + pesan error generik."""
    data = request.get_json(silent=True) or {}
    username, password = data.get("username"), data.get("password")
    if not valid_username(username) or not isinstance(password, str):
        return jsonify(error="username atau password salah"), 401
    init_db()
    row = get_db().execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return jsonify(error="username atau password salah"), 401
    return jsonify(message="login berhasil")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))  # nosec B104 - container
