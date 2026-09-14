def test_cart_update_and_remove_item(client, client_headers):
    r = client.post(
        "/api/v1/cart/items",
        json={"variant_id": 1, "quantity": 1},
        headers=client_headers,
    )
    assert r.status_code == 200, r.text

    r = client.patch(
        "/api/v1/cart/items/1",
        json={"variant_id": 1, "quantity": 3},
        headers=client_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["details"][0]["quantity"] == 3
    assert body["total"] == 180.0 * 3

    r = client.delete("/api/v1/cart/items/1", headers=client_headers)
    assert r.status_code == 200, r.text
    assert r.json()["details"] == []
    assert r.json()["total"] == 0


def test_cart_update_missing_item_404(client, client_headers):
    r = client.patch(
        "/api/v1/cart/items/99999",
        json={"variant_id": 99999, "quantity": 2},
        headers=client_headers,
    )
    assert r.status_code == 404


def test_purchase_from_cart_creates_sale_and_payment(client, client_headers):
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 2, "quantity": 1},
        headers=client_headers,
    )
    r = client.post(
        "/api/v1/cart/purchase",
        json={"branch_id": 1, "payment_method": "card"},
        headers=client_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    sale = body["sale"]
    payment = body["payment"]

    assert sale["status"] == "PENDING"
    assert sale["total_amount"] == 180.0
    assert sale["client_id"] is not None
    assert payment["sale_id"] == sale["id"]
    assert payment["gateway_reference"].startswith("mock_")

    r = client.get("/api/v1/cart", headers=client_headers)
    assert r.json()["details"] == []
    assert r.json()["total"] == 0

    r = client.post(
        "/api/v1/payments/confirm",
        json={"gateway_reference": payment["gateway_reference"]},
        headers=client_headers,
    )
    assert r.status_code == 200, r.text

    r = client.get(f"/api/v1/sales/{sale['id']}", headers=client_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "PAID"


def test_purchase_requires_stock_and_nonempty(client, client_headers):
    r = client.post(
        "/api/v1/cart/purchase",
        json={"branch_id": 1},
        headers=client_headers,
    )
    assert r.status_code == 422
