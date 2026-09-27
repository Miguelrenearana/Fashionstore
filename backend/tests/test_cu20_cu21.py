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


def test_cart_items_expose_catalogue_data(client, client_headers):
    """CU-20: sin nombre, foto ni talla el carrito movil es ilegible."""
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 1, "quantity": 2},
        headers=client_headers,
    )
    body = client.get("/api/v1/cart", headers=client_headers).json()
    detail = body["details"][0]

    assert detail["garment_id"] is not None
    assert detail["garment_name"]
    assert detail["sku"]
    assert detail["size_name"]
    assert detail["color_name"]
    assert detail["image_url"]
    assert detail["line_total"] == detail["unit_price"] * 2
    assert body["items_count"] == 2
    assert body["total"] == detail["line_total"]


def test_sale_exposes_created_at_items_count_and_details(client, client_headers):
    """CU-22: el historial necesita created_at, items_count y el detalle leido."""
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 1, "quantity": 2},
        headers=client_headers,
    )
    sale_id = client.post(
        "/api/v1/cart/purchase",
        json={"branch_id": 1, "payment_method": "card"},
        headers=client_headers,
    ).json()["sale"]["id"]

    sale = client.get(f"/api/v1/sales/{sale_id}", headers=client_headers).json()

    assert sale["invoice_number"]
    assert sale["created_at"] is not None
    assert sale["items_count"] == 2
    detail = sale["details"][0]
    assert detail["quantity"] == 2
    assert detail["line_total"] == detail["unit_price"] * 2
    assert detail["garment_name"]
    assert detail["size_name"]
    assert detail["color_name"]
    assert detail["image_url"]


def test_sales_mine_only_returns_the_own_client_sales(client, client_headers):
    """CU-22: ?mine=true no debe exponer ventas de otros clientes."""
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": 1, "quantity": 1},
        headers=client_headers,
    )
    mine = client.get(
        "/api/v1/sales", params={"mine": "true"}, headers=client_headers
    ).json()

    assert isinstance(mine, list)
    assert len(mine) == 1
    assert mine[0]["client_id"] is not None
    assert all(s["details"] for s in mine)
