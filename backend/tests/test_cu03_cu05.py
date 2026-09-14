from conftest import unique_email

from app.core.database import SessionLocal
from app.models.analytics import Notification


def _recovery_token_from_db(db, email: str) -> str:
    row = (
        db.query(Notification)
        .join(Notification.user)
        .filter(Notification.type == "password_reset", Notification.user.has(email=email))
        .order_by(Notification.id.desc())
        .first()
    )
    assert row, "no password_reset notification found"
    return row.body.split(": ")[-1].strip()


def _register_client(client, email: str) -> dict:
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "clientpass1",
            "first_name": "Ana",
            "last_name": "Lopez",
            "phone": "700-1234",
            "birth_date": "1998-03-10",
        },
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_register_client_success(client, cleanup_users):
    email = cleanup_users(unique_email("test-cu05"))
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "clientpass1",
            "first_name": "Ana",
            "last_name": "Lopez",
            "phone": "700-1234",
            "birth_date": "1998-03-10",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"

    r = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "clientpass1"},
    )
    assert r.status_code == 200


def test_register_duplicate_rejected(client, cleanup_users):
    email = cleanup_users(unique_email("test-cu05"))
    payload = {
        "email": email,
        "password": "clientpass1",
        "first_name": "Ana",
        "last_name": "Lopez",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 200
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 403


def test_get_my_profile(client, cleanup_users):
    email = cleanup_users(unique_email("test-cu05"))
    headers = _register_client(client, email)
    r = client.get("/api/v1/clients/me", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == email
    assert body["first_name"] == "Ana"
    assert body["last_name"] == "Lopez"
    assert body["points"] == 0
    assert body["id"]


def test_update_profile(client, cleanup_users):
    email = cleanup_users(unique_email("test-cu05"))
    headers = _register_client(client, email)
    r = client.patch(
        "/api/v1/clients/me",
        json={"first_name": "AnaMaria", "phone": "600-0001"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["first_name"] == "AnaMaria"
    assert body["phone"] == "600-0001"

    r = client.get("/api/v1/clients/me", headers=headers)
    assert r.json()["first_name"] == "AnaMaria"


def test_profile_requires_client_role(client, admin_headers):
    r = client.get("/api/v1/clients/me", headers=admin_headers)
    assert r.status_code == 404


def test_forgot_password_creates_token_and_reset(client, cleanup_users):
    email = cleanup_users(unique_email("test-cu03"))
    _register_client(client, email)
    r = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert r.status_code == 200, r.text
    assert "token" in r.json()["message"].lower()

    db = SessionLocal()
    try:
        token = _recovery_token_from_db(db, email)
    finally:
        db.close()

    r = client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "password": "nuevapass1"},
    )
    assert r.status_code == 200, r.text

    r = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "nuevapass1"},
    )
    assert r.status_code == 200


def test_forgot_password_unknown_email_still_ok(client):
    r = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": f"noexiste-{unique_email().split('@')[0]}@fashionstore.dev"},
    )
    assert r.status_code == 200


def test_reset_with_bad_token_rejected(client):
    r = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "token-invalido-0000", "password": "nuevapass1"},
    )
    assert r.status_code == 401
