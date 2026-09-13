from conftest import unique_email


def test_login_success(client):
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@fashionstore.dev", "password": "Admin123!"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_wrong_password_rejected(client):
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@fashionstore.dev", "password": "WrongPass!"},
    )
    assert r.status_code == 401


def test_me_requires_token(client):
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401


def test_me_returns_own_roles(client, admin_headers):
    r = client.get("/api/v1/users/me", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "admin@fashionstore.dev"
    assert "ADMIN" in [role["name"] for role in body["roles"]]


def test_list_users_forbidden_for_client(client, client_headers):
    r = client.get("/api/v1/users", headers=client_headers)
    assert r.status_code == 403


def test_list_users_ok_for_admin(client, admin_headers):
    r = client.get("/api/v1/users", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_roles_admin(client, admin_headers):
    r = client.get("/api/v1/users/roles", headers=admin_headers)
    assert r.status_code == 200
    names = [role["name"] for role in r.json()]
    assert {"ADMIN", "MANAGER", "CLIENT"}.issubset(names)


def test_create_user_requires_admin(client, client_headers):
    r = client.post(
        "/api/v1/users",
        json={"email": unique_email(), "password": "secret123", "roles": ["CLIENT"]},
        headers=client_headers,
    )
    assert r.status_code == 403


def test_create_user_and_employee_flow(client, admin_headers, cleanup_users):
    email = cleanup_users(unique_email("test-cu02"))
    r = client.post(
        "/api/v1/users",
        json={"email": email, "password": "secret123", "phone": "555-0100", "roles": ["CASHIER"]},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    user = r.json()
    assert user["email"] == email
    assert "CASHIER" in [role["name"] for role in user["roles"]]

    r = client.post(
        f"/api/v1/users/{user['id']}/employee",
        json={
            "first_name": "Carlos",
            "last_name": "Perez",
            "branch_id": 1,
            "hire_date": "2024-01-15",
        },
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    emp = r.json()
    assert emp["user_id"] == user["id"]
    assert emp["branch"]["id"] == 1


def test_duplicate_email_conflict(client, admin_headers, cleanup_users):
    email = cleanup_users(unique_email("test-cu01"))
    payload = {"email": email, "password": "secret123", "roles": ["CLIENT"]}
    r = client.post("/api/v1/users", json=payload, headers=admin_headers)
    assert r.status_code == 200
    r = client.post("/api/v1/users", json=payload, headers=admin_headers)
    assert r.status_code == 409


def test_unknown_role_rejected(client, admin_headers, cleanup_users):
    email = cleanup_users(unique_email("test-cu01"))
    r = client.post(
        "/api/v1/users",
        json={"email": email, "password": "secret123", "roles": ["GOD"]},
        headers=admin_headers,
    )
    assert r.status_code == 422
