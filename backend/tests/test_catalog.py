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
