import uuid

from sqlalchemy import text

from app.core.database import SessionLocal
from app.models.inventory import Inventory


def test_list_products_admin(client, admin_headers):
    r = client.get("/api/v1/products", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_products_forbidden_client(client, client_headers):
    r = client.get("/api/v1/products", headers=client_headers)
    assert r.status_code == 403


def _create_garment(client, admin_headers, name, prefix):
    sku = f"{prefix}-{uuid.uuid4().hex[:6]}"
    r = client.post(
        "/api/v1/products",
        json={
            "category_id": 1,
            "name": name,
            "description": "Test",
            "base_price": 100.0,
            "is_ar_enabled": False,
            "variants": [{"size_id": 1, "color_id": 1, "sku": sku, "price": 100.0}],
        },
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_update_product_success(client, admin_headers):
    garment = _create_garment(client, admin_headers, "Test Garment", "TEST-001")

    r = client.patch(
        f"/api/v1/products/{garment['id']}",
        json={"name": "Updated Name", "base_price": 150.0},
        headers=admin_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Updated Name"
    assert data["base_price"] == 150.0


def test_update_product_partial(client, admin_headers):
    garment = _create_garment(client, admin_headers, "Partial Test", "PART-001")

    r = client.patch(
        f"/api/v1/products/{garment['id']}",
        json={"base_price": 75.0},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["base_price"] == 75.0
    assert r.json()["name"] == "Partial Test"


def test_update_product_404(client, admin_headers):
    r = client.patch(
        "/api/v1/products/999999",
        json={"name": "No Existe"},
        headers=admin_headers,
    )
    assert r.status_code == 404


def test_update_product_forbidden_client(client, client_headers):
    r = client.patch(
        "/api/v1/products/1",
        json={"name": "Hack"},
        headers=client_headers,
    )
    assert r.status_code == 403


def test_update_product_invalid_category(client, admin_headers):
    garment = _create_garment(client, admin_headers, "Cat Test", "CAT-001")

    r = client.patch(
        f"/api/v1/products/{garment['id']}",
        json={"category_id": 999999},
        headers=admin_headers,
    )
    assert r.status_code == 404


def test_delete_product_success(client, admin_headers):
    garment = _create_garment(client, admin_headers, "To Delete", "DEL-001")

    r = client.delete(f"/api/v1/products/{garment['id']}", headers=admin_headers)
    assert r.status_code == 204

    r = client.get(f"/api/v1/products/{garment['id']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_delete_product_404(client, admin_headers):
    r = client.delete("/api/v1/products/999999", headers=admin_headers)
    assert r.status_code == 404


def test_delete_product_forbidden(client, client_headers):
    r = client.delete("/api/v1/products/1", headers=client_headers)
    assert r.status_code == 403


def test_delete_product_with_reserved_stock(client, admin_headers):
    garment = _create_garment(client, admin_headers, "Reserved Stock", "RES-001")
    variants = client.get(
        f"/api/v1/products/{garment['id']}/variants", headers=admin_headers
    ).json()
    variant_id = variants[0]["id"]

    with SessionLocal() as db:
        branch_id = db.execute(text("SELECT id FROM sucursal LIMIT 1")).scalar()
        db.add(
            Inventory(
                branch_id=branch_id,
                variant_id=variant_id,
                quantity=10,
                reserved_quantity=3,
            )
        )
        db.commit()

    r = client.delete(f"/api/v1/products/{garment['id']}", headers=admin_headers)
    assert r.status_code == 422

    r = client.get(f"/api/v1/products/{garment['id']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["is_active"] is True