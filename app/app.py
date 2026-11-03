import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = "rahasia123"

def get_db():
    return sqlite3.connect("app.db")

@app.post("/register")
def register():
    data = request.get_json()
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password_hash TEXT)")
    db.execute("INSERT INTO users VALUES ('%s', '%s')" % (data["username"], data["password"]))
    db.commit()
    return jsonify(message="registrasi berhasil"), 201

@app.post("/login")
def login():
    data = request.get_json()
    db = get_db()
    query = f"SELECT * FROM users WHERE username = '{data['username']}' AND password_hash = '{data['password']}'"
    user = db.execute(query).fetchone()
    if user:
        return jsonify(message="login berhasil")
    return jsonify(error="user " + data["username"] + " tidak ditemukan"), 401

@app.get("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
