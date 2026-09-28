from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models.reservation import Reservation
from app.models.user import Client, Employee, User


def _staff_headers(client, email, password):
    response = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _reservation(db, branch_id):
    owner = db.query(Client).join(User).filter(User.email == "client@fashionstore.dev").one()
    reservation = Reservation(
        client_id=owner.id,
        branch_id=branch_id,
        pickup_code=uuid4().hex[:16],
        status="PENDING",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        total_amount=0,
    )
    db.add(reservation)
    db.commit()
    return reservation.id


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

    r = client.patch(
        f"/api/v1/reservations/{reservation_id}/status",
        json={"status": "COMPLETED"},
        headers=admin_headers,
    )
    assert r.status_code == 409
    assert client.get(
        f"/api/v1/reservations/{reservation_id}", headers=client_headers
    ).json()["status"] == "IN_TRIAL"


def test_employees_only_list_read_and_transition_their_branch(client, db, admin_headers):
    manager = db.query(Employee).join(User).filter(User.email == "manager@fashionstore.dev").one()
    cashier = db.query(Employee).join(User).filter(User.email == "cashier@fashionstore.dev").one()
    other_branch = 2 if manager.branch_id == 1 else 1
    cashier.branch_id = other_branch
    db.commit()
    own_id = _reservation(db, manager.branch_id)
    other_id = _reservation(db, other_branch)
    manager_headers = _staff_headers(client, "manager@fashionstore.dev", "Manager123!")
    cashier_headers = _staff_headers(client, "cashier@fashionstore.dev", "Cashier123!")

    for headers, visible, hidden in (
        (manager_headers, own_id, other_id),
        (cashier_headers, other_id, own_id),
    ):
        listed = client.get("/api/v1/reservations", headers=headers)
        assert listed.status_code == 200, listed.text
        ids = {item["id"] for item in listed.json()}
        assert visible in ids and hidden not in ids
        assert all(item["branch_id"] == (manager.branch_id if visible == own_id else other_branch)
                   for item in listed.json())
        assert client.get(f"/api/v1/reservations/{hidden}", headers=headers).status_code == 403
        assert client.patch(
            f"/api/v1/reservations/{hidden}/status",
            json={"status": "PREPARED"}, headers=headers,
        ).status_code == 403
        assert client.post(
            "/api/v1/sales",
            json={"branch_id": other_branch if hidden == other_id else manager.branch_id,
                  "reservation_id": hidden, "payment_method": "card"},
            headers=headers,
        ).status_code == 403
        assert client.get(f"/api/v1/reservations/{visible}", headers=headers).status_code == 200
        assert client.patch(
            f"/api/v1/reservations/{visible}/status",
            json={"status": "PREPARED"}, headers=headers,
        ).status_code == 200

    assert client.get(f"/api/v1/reservations/{own_id}", headers=admin_headers).status_code == 200
    assert client.get(f"/api/v1/reservations/{other_id}", headers=admin_headers).status_code == 200


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
