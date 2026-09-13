from app.core.database import SessionLocal
from app.models.inventory import Inventory


def _reserved(branch_id: int, variant_id: int) -> int:
    db = SessionLocal()
    try:
        inv = db.query(Inventory).filter(
            Inventory.branch_id == branch_id, Inventory.variant_id == variant_id
        ).first()
        return inv.reserved_quantity if inv else -1
    finally:
        db.close()


def test_checkout_creates_reservation_and_clears_cart(client, client_headers):
    r = client.post(
        "/api/v1/cart/items",
        json={"variant_id": 1, "quantity": 1},
        headers=client_headers,
    )
    assert r.status_code == 200, r.text

    r = client.post("/api/v1/cart/checkout", json={"branch_id": 1}, headers=client_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "PENDING"
    assert data["pickup_code"]
    assert data["total_amount"] == 180.0
    assert data["branch_id"] == 1

    r = client.get("/api/v1/cart", headers=client_headers)
    assert r.json()["details"] == []
    assert r.json()["total"] == 0

    r = client.get("/api/v1/reservations/me", headers=client_headers)
    ids = [res["id"] for res in r.json()]
    assert data["id"] in ids


def test_client_cancel_own_reservation_releases_stock(client, client_headers):
    before = _reserved(1, 2)
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 2, "quantity": 1},
        headers=client_headers,
    )
    r = client.post("/api/v1/cart/checkout", json={"branch_id": 1}, headers=client_headers)
    reservation_id = r.json()["id"]
    assert _reserved(1, 2) == before + 1

    r = client.patch(
        f"/api/v1/reservations/{reservation_id}/status",
        json={"status": "CANCELLED", "comment": "ya no lo quiero"},
        headers=client_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "CANCELLED"
    assert _reserved(1, 2) == before


def test_sale_from_reservation(client, client_headers, admin_headers):
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 1, "quantity": 2},
        headers=client_headers,
    )
    r = client.post("/api/v1/cart/checkout", json={"branch_id": 1}, headers=client_headers)
    reservation_id = r.json()["id"]

    for status in ("PREPARED", "IN_TRIAL"):
        r = client.patch(
            f"/api/v1/reservations/{reservation_id}/status",
            json={"status": status},
            headers=admin_headers,
        )
        assert r.status_code == 200, r.text

    r = client.post(
        "/api/v1/sales",
        json={"branch_id": 1, "reservation_id": reservation_id, "payment_method": "card"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    sale = r.json()
    assert sale["reservation_id"] == reservation_id
    assert sale["total_amount"] == 360.0
    assert sale["status"] == "PENDING"

    r = client.get(f"/api/v1/reservations/{reservation_id}", headers=client_headers)
    assert r.json()["status"] == "COMPLETED"

    r = client.get(f"/api/v1/sales/{sale['id']}", headers=client_headers)
    assert r.status_code == 200


def test_direct_sale_requires_staff(client, client_headers, admin_headers):
    r = client.post(
        "/api/v1/sales",
        json={"branch_id": 1, "items": [{"variant_id": 1, "quantity": 1}]},
        headers=client_headers,
    )
    assert r.status_code == 403

    r = client.post(
        "/api/v1/sales",
        json={"branch_id": 1, "items": [{"variant_id": 1, "quantity": 1}]},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "PENDING"


def test_payment_initiate_confirm_and_refund(client, admin_headers):
    r = client.post(
        "/api/v1/sales",
        json={"branch_id": 1, "items": [{"variant_id": 2, "quantity": 1}]},
        headers=admin_headers,
    )
    sale_id = r.json()["id"]

    r = client.post(f"/api/v1/payments/initiate?sale_id={sale_id}&method=card", headers=admin_headers)
    assert r.status_code == 200, r.text
    ref = r.json()["gateway_reference"]
    assert ref.startswith("mock_")

    r = client.post("/api/v1/payments/confirm", json={"gateway_reference": ref}, headers=admin_headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "COMPLETED"

    r = client.get(f"/api/v1/sales/{sale_id}", headers=admin_headers)
    assert r.json()["status"] == "PAID"
    assert r.json()["paid_at"] is not None

    r = client.post(f"/api/v1/payments/refund?gateway_reference={ref}", headers=admin_headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "REFUNDED"

    r = client.get(f"/api/v1/sales/{sale_id}", headers=admin_headers)
    assert r.json()["status"] == "REFUNDED"
