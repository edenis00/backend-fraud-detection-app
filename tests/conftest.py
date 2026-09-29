import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


test_database_url = os.getenv("TEST_DATABASE_URL")

if not test_database_url:
    test_database_url = "sqlite:///./test.db"
    os.environ["TEST_DATABASE_URL"] = test_database_url

# Overrides the development database before application modules load.
os.environ["DATABASE_URL"] = test_database_url

import app.database.models
from app.database.base import Base
from app.database.session import SessionLocal, engine, get_db
from app.main import app


@pytest.fixture(autouse=True)
def reset_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    payload = {
        "full_name": "Test Fraud Analyst",
        "email": "analyst@example.com",
        "password": "secure-test-password",
    }
    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    return payload


@pytest.fixture
def auth_headers(client, registered_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}