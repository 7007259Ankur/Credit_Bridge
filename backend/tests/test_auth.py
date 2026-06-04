"""Basic auth endpoint tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# In-memory SQLite for tests
SQLITE_URL = "sqlite:///./test.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login():
    payload = {
        "email": "test@example.com",
        "password": "Test1234!",
        "full_name": "Test User",
        "role": "applicant",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data

    r2 = client.post("/api/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_login_wrong_password():
    r = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert r.status_code == 401
