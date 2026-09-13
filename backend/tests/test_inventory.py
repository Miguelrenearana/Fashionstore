from random import randint


def test_list_inventory_for_branch(client, admin_headers):
    branches = client.get("/api/v1/locations/branches").json()
    branch_id = branches[0]["id"]
    r = client.get(f"/api/v1/inventory?branch_id={branch_id}", headers=admin_headers)
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) >= 1
    row = rows[0]
    assert row["variant"]["sku"]
    assert row["variant"]["size_name"]
    assert row["variant"]["color_name"]


def test_inventory_forbidden_for_client(client, client_headers):
    branches = client.get("/api/v1/locations/branches").json()
    branch_id = branches[0]["id"]
    r = client.get(f"/api/v1/inventory?branch_id={branch_id}", headers=client_headers)
    assert r.status_code == 403


def test_adjust_inventory(client, admin_headers):
    branches = client.get("/api/v1/locations/branches").json()
    inventory = client.get(
        f"/api/v1/inventory?branch_id={branches[0]['id']}", headers=admin_headers
    ).json()
    base = inventory[0]
    delta = randint(1, 5)
    r = client.patch(
        f"/api/v1/inventory/{base['branch_id']}/{base['variant_id']}/adjust",
        json={"quantity": delta, "reason": "test"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["quantity"] == base["quantity"] + delta


def test_adjust_negative_stock_rejected(client, admin_headers):
    branches = client.get("/api/v1/locations/branches").json()
    inventory = client.get(
        f"/api/v1/inventory?branch_id={branches[0]['id']}", headers=admin_headers
    ).json()
    base = inventory[0]
    r = client.patch(
        f"/api/v1/inventory/{base['branch_id']}/{base['variant_id']}/adjust",
        json={"quantity": -99999},
        headers=admin_headers,
    )
    assert r.status_code == 422


def test_list_movements(client, admin_headers):
    branches = client.get("/api/v1/locations/branches").json()
    inventory = client.get(
        f"/api/v1/inventory?branch_id={branches[0]['id']}", headers=admin_headers
    ).json()
    base = inventory[0]
    client.patch(
        f"/api/v1/inventory/{base['branch_id']}/{base['variant_id']}/adjust",
        json={"quantity": 1, "reason": "mov test"},
        headers=admin_headers,
    )
    r = client.get(
        f"/api/v1/inventory/movements?branch_id={base['branch_id']}&variant_id={base['variant_id']}",
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()[0]["movement_type"] in {"IN", "OUT"}
