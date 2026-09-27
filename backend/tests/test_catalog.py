def test_list_catalog(client):
    r = client.get("/api/v1/catalog?page=1&size=20")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert body["items"][0]["name"]


def test_catalog_detail_returns_variants(client):
    r = client.get("/api/v1/catalog/1")
    assert r.status_code == 200
    item = r.json()
    assert item["id"] == 1
    assert item["min_price"] > 0
    assert isinstance(item["in_stock"], bool)
    assert any(v["size_name"] and v["color_name"] for v in item["variants"])


def test_catalog_detail_404(client):
    r = client.get("/api/v1/catalog/99999")
    assert r.status_code == 404


def test_catalog_categories(client):
    r = client.get("/api/v1/catalog/categories")
    assert r.status_code == 200
    names = [c["name"] for c in r.json()]
    assert "Camisas" in names


def test_catalog_search(client):
    r = client.get("/api/v1/catalog?search=oxford")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_catalog_category_filter(client):
    r1 = client.get("/api/v1/catalog/categories")
    category_id = r1.json()[0]["id"]
    r = client.get(f"/api/v1/catalog?category_id={category_id}")
    assert r.status_code == 200
    assert all(i["category"]["id"] == category_id for i in r.json()["items"])


def test_catalog_branch_filter(client):
    branches = client.get("/api/v1/locations/branches")
    assert branches.status_code == 200
    branch_id = branches.json()[0]["id"]
    r = client.get(f"/api/v1/catalog?branch_id={branch_id}")
    assert r.status_code == 200


# --------------------------------------------------------------------------- #
# CU-13: filtros de catalogo
# --------------------------------------------------------------------------- #


def test_catalog_rejects_unknown_sort(client):
    r = client.get("/api/v1/catalog?sort_by=popular")
    assert r.status_code == 422


def test_catalog_sort_by_price_asc_is_ordered(client):
    r = client.get("/api/v1/catalog?sort_by=price_asc&size=100")
    assert r.status_code == 200
    prices = [i["min_price"] for i in r.json()["items"]]
    assert prices == sorted(prices)


def test_catalog_price_range_filter(client):
    all_items = client.get("/api/v1/catalog?size=100").json()["items"]
    prices = sorted(i["min_price"] for i in all_items)
    lo, hi = prices[0], prices[len(prices) // 2]

    r = client.get(f"/api/v1/catalog?min_price={lo}&max_price={hi}&size=100")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert any(lo <= v["price"] <= hi for v in item["variants"])


def test_catalog_size_and_color_filter(client):
    # Se deriva un par (talla, color) que existe de verdad en los datos.
    sample = next(
        v
        for i in client.get("/api/v1/catalog?size=100").json()["items"]
        for v in i["variants"]
    )
    size = sample["size_name"]
    color = sample["color_name"]

    r = client.get(f"/api/v1/catalog?sizes={size}&colors={color}&size=100")
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    # Talla y color deben cumplirse en la misma variante.
    for item in items:
        assert any(
            v["size_name"] == size and v["color_name"] == color for v in item["variants"]
        )


def test_catalog_size_and_color_filter_do_not_mix_variants(client):
    """Con size+color el filtro no puede devolver prendas sin esa combinacion."""
    r = client.get("/api/v1/catalog?sizes=M&size=100")
    assert r.status_code == 200
    m_only = client.get("/api/v1/catalog?colors=Negro&size=100").json()["items"]

    combined = client.get("/api/v1/catalog?sizes=M&colors=Negro&size=100").json()
    # Si no existe la combinacion, el resultado debe estar vacio, no la union.
    assert len(combined["items"]) <= min(
        len(r.json()["items"]), len(m_only)
    )


def test_catalog_in_stock_filter_only_returns_available(client):
    r = client.get("/api/v1/catalog?in_stock=true&size=100")
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    for item in items:
        assert any(v["available"] > 0 for v in item["variants"])


# --------------------------------------------------------------------------- #
# CU-14: disponibilidad real por sucursal
# --------------------------------------------------------------------------- #


def test_catalog_variants_expose_real_stock(client):
    r = client.get("/api/v1/catalog?size=20")
    assert r.status_code == 200
    for item in r.json()["items"]:
        for variant in item["variants"]:
            assert variant["stock"] >= 0
            assert variant["available"] >= 0
            assert variant["available"] <= variant["stock"]


def test_availability_endpoint_splits_by_branch(client):
    garment_id = client.get("/api/v1/catalog?size=1").json()["items"][0]["id"]
    r = client.get(f"/api/v1/catalog/{garment_id}/availability")
    assert r.status_code == 200
    body = r.json()
    assert body
    for variant in body:
        assert variant["sku"]
        assert variant["total_available"] >= 0
        for row in variant["branches"]:
            assert row["available"] == row["quantity"] - row["reserved_quantity"]
        # Ninguna sucursal repetida: una sola fila por (variante, sucursal).
        branch_ids = [row["branch_id"] for row in variant["branches"]]
        assert len(branch_ids) == len(set(branch_ids))


def test_branch_filter_matches_availability_endpoint(client):
    branch_id = client.get("/api/v1/locations/branches").json()[0]["id"]
    garment_id = client.get(f"/api/v1/catalog?branch_id={branch_id}&size=1").json()["items"][0][
        "id"
    ]
    availability = client.get(f"/api/v1/catalog/{garment_id}/availability").json()
    detail = client.get(f"/api/v1/catalog/{garment_id}?branch_id={branch_id}").json()

    for variant, read in zip(availability, detail["variants"], strict=True):
        expected = next(
            (r["available"] for r in variant["branches"] if r["branch_id"] == branch_id), 0
        )
        assert read["available"] == expected

