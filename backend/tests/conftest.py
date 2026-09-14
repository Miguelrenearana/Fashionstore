import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.analytics import BrowsingHistory, Notification
from app.models.user import Client, Employee, PasswordReset, User


@pytest.fixture
def client():
    c = TestClient(app)
    yield c


def _login_headers(client, email, password):
    r = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin_headers(client):
    return _login_headers(client, "admin@fashionstore.dev", "Admin123!")


@pytest.fixture
def client_headers(client):
    return _login_headers(client, "client@fashionstore.dev", "Client123!")


def unique_email(prefix: str = "test-cu01") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@fashionstore.dev"


@pytest.fixture
def cleanup_users():
    created: list[str] = []

    def _track(email: str) -> str:
        created.append(email)
        return email

    yield _track

    db = SessionLocal()
    try:
        for email in created:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                continue
            db.query(Notification).filter(Notification.user_id == user.id).delete()
            db.query(PasswordReset).filter(PasswordReset.user_id == user.id).delete()
            client = db.query(Client).filter(Client.user_id == user.id).first()
            if client:
                db.query(BrowsingHistory).filter(BrowsingHistory.client_id == client.id).delete()
            db.query(Employee).filter(Employee.user_id == user.id).delete()
            db.delete(user)
        db.commit()
    finally:
        db.close()
