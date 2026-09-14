def test_client_consults_own_reservation(client, client_headers):
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 1, "quantity": 1},
        headers=client_headers,
    )
    r = client.post("/api/v1/cart/checkout", json={"branch_id": 1}, headers=client_headers)
    reservation_id = r.json()["id"]

    r = client.get(f"/api/v1/reservations/{reservation_id}", headers=client_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == reservation_id
    assert body["status"] == "PENDING"
    assert body["pickup_code"]
    assert body["total_amount"] > 0


def test_client_cannot_read_staff_list(client, client_headers):
    r = client.get("/api/v1/reservations", headers=client_headers)
    assert r.status_code == 403


def test_staff_lists_reservations_by_status(client, admin_headers):
    r = client.get("/api/v1/reservations", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.get("/api/v1/reservations?status=prepared", headers=admin_headers)
    assert r.status_code == 200
    assert all(item["status"] == "PREPARED" for item in r.json())


def test_staff_prepares_reservation(client, client_headers, admin_headers):
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 2, "quantity": 1},
        headers=client_headers,
    )
    r = client.post("/api/v1/cart/checkout", json={"branch_id": 1}, headers=client_headers)
    reservation_id = r.json()["id"]

    r = client.patch(
        f"/api/v1/reservations/{reservation_id}/status",
        json={"status": "PREPARED", "comment": "prendas listas"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "PREPARED"

    r = client.patch(
        f"/api/v1/reservations/{reservation_id}/status",
        json={"status": "IN_TRIAL"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "IN_TRIAL"


def test_client_updates_status_but_only_cancel(client, client_headers, admin_headers):
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 2, "quantity": 1},
        headers=client_headers,
    )
    r = client.post("/api/v1/cart/checkout", json={"branch_id": 1}, headers=client_headers)
    reservation_id = r.json()["id"]

    r = client.patch(
        f"/api/v1/reservations/{reservation_id}/status",
        json={"status": "PREPARED"},
        headers=client_headers,
    )
    assert r.status_code == 403

    r = client.patch(
        f"/api/v1/reservations/{reservation_id}/status",
        json={"status": "CANCELLED"},
        headers=client_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "CANCELLED"
