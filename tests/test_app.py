"""Unit test + security test sederhana."""
import pytest

from app.app import app


@pytest.fixture(name="client")
def fixture_client(tmp_path, monkeypatch):
    """Client test dengan database sementara."""
    monkeypatch.setattr("app.app.DB_PATH", str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    """Health check harus 200."""
    assert client.get("/health").status_code == 200


def test_register_login(client):
    """Alur normal registrasi dan login."""
    assert client.post("/register", json={"username": "budi", "password": "Rahasia123"}).status_code == 201
    assert client.post("/login", json={"username": "budi", "password": "Rahasia123"}).status_code == 200


def test_wrong_password(client):
    """Password salah ditolak."""
    client.post("/register", json={"username": "budi", "password": "Rahasia123"})
    assert client.post("/login", json={"username": "budi", "password": "salah"}).status_code == 401


def test_sql_injection_rejected(client):
    """Payload SQLi klasik tidak boleh bypass login."""
    resp = client.post("/login", json={"username": "admin' OR '1'='1", "password": "x"})
    assert resp.status_code == 401


def test_security_headers(client):
    """Security headers wajib ada."""
    h = client.get("/health").headers
    assert h["X-Frame-Options"] == "DENY"
    assert h["X-Content-Type-Options"] == "nosniff"
