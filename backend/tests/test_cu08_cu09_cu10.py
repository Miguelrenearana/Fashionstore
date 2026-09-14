import uuid


def _uniq(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:6]}"


def test_options_read_lists(client, client_headers):
    for path in ("sizes", "colors", "seasons", "collections"):
        r = client.get(f"/api/v1/catalog/options/{path}", headers=client_headers)
        assert r.status_code == 200, r.text
        assert isinstance(r.json(), list)


def test_create_size_admin(client, admin_headers):
    name = _uniq("XXL3")
    r = client.post(
        "/api/v1/catalog/options/sizes",
        json={"name": name},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["name"] == name


def test_create_color_admin(client, admin_headers):
    r = client.post(
        "/api/v1/catalog/options/colors",
        json={"name": _uniq("Azul Marino"), "hex_code": "#000080"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["hex_code"] == "#000080"


def test_create_category_and_patch(client, admin_headers):
    r = client.post(
        "/api/v1/catalog/options/categories",
        json={"name": _uniq("Jeans"), "description": "Pantalones de mezclilla"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    cat = r.json()
    r = client.patch(
        f"/api/v1/catalog/options/categories/{cat['id']}",
        json={"description": "Actualizado"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["description"] == "Actualizado"


def test_mutations_require_admin(client, client_headers):
    r = client.post(
        "/api/v1/catalog/options/sizes",
        json={"name": _uniq("XXXL")},
        headers=client_headers,
    )
    assert r.status_code == 403


def test_season_and_collection_flow(client, admin_headers):
    r = client.post(
        "/api/v1/catalog/options/seasons",
        json={"name": _uniq("Primavera 2027")},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    season = r.json()

    r = client.post(
        "/api/v1/catalog/options/collections",
        json={"season_id": season["id"], "name": _uniq("Colección Floral"), "launch_year": 2027},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    col = r.json()
    assert col["season_id"] == season["id"]

    r = client.patch(
        f"/api/v1/catalog/options/collections/{col['id']}",
        json={"launch_year": 2028},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["launch_year"] == 2028


def test_suppliers_list_and_crud(client, admin_headers):
    r = client.get("/api/v1/suppliers", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    name = _uniq("Industrias Textiles")
    r = client.post(
        "/api/v1/suppliers",
        json={"company_name": name, "contact_name": "Juan Perez", "phone": "700-0000"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    supplier = r.json()
    assert supplier["company_name"] == name

    r = client.patch(
        f"/api/v1/suppliers/{supplier['id']}",
        json={"contact_name": "Ana Maria"},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["contact_name"] == "Ana Maria"

    r = client.patch(
        f"/api/v1/suppliers/{supplier['id']}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert r.status_code == 200
    r = client.get("/api/v1/suppliers", headers=admin_headers)
    names = [s["company_name"] for s in r.json()]
    assert name not in names


def test_supplier_mutation_requires_admin(client, client_headers):
    r = client.post(
        "/api/v1/suppliers",
        json={"company_name": _uniq("Test")},
        headers=client_headers,
    )
    assert r.status_code == 403
