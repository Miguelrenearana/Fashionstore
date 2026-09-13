from app.core.database import SessionLocal
from app.models.user import Branch


def test_list_cities(client):
    r = client.get("/api/v1/locations/cities")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_list_branches(client):
    r = client.get("/api/v1/locations/branches")
    assert r.status_code == 200
    branches = r.json()
    assert len(branches) >= 1
    assert any(b["city"] and b["city"]["name"] for b in branches)


def test_create_branch_forbidden_for_client(client, client_headers):
    r = client.post(
        "/api/v1/locations/branches",
        json={"city_id": 1, "name": "Sucursal X", "address": "Calle 1"},
        headers=client_headers,
    )
    assert r.status_code == 403


def test_create_branch_admin(client, admin_headers):
    cities = client.get("/api/v1/locations/cities").json()
    branch_id = None
    try:
        r = client.post(
            "/api/v1/locations/branches",
            json={
                "city_id": cities[0]["id"],
                "name": "Sucursal Test",
                "address": "Av. Siempre 123",
            },
            headers=admin_headers,
        )
        assert r.status_code == 200, r.text
        branch = r.json()
        branch_id = branch["id"]
        assert branch["name"] == "Sucursal Test"
        assert branch["city"]["id"] == cities[0]["id"]
    finally:
        db = SessionLocal()
        try:
            if branch_id is not None:
                branch = db.get(Branch, branch_id)
                if branch:
                    db.delete(branch)
                    db.commit()
        finally:
            db.close()


def test_create_branch_city_not_found(client, admin_headers):
    r = client.post(
        "/api/v1/locations/branches",
        json={"city_id": 99999, "name": "Sucursal X", "address": "Calle 1"},
        headers=admin_headers,
    )
    assert r.status_code == 404
