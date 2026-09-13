from app.core.database import SessionLocal
from app.models.inventory import ProductEmbedding


def _ensure_embeddings():
    db = SessionLocal()
    try:
        if db.query(ProductEmbedding).count() == 0:
            from app.tasks.recommendation_batch import recompute_embeddings

            recompute_embeddings()
    finally:
        db.close()


def _variant_ids(client, client_headers) -> list[int]:
    r = client.get("/api/v1/catalog", headers=client_headers)
    assert r.status_code == 200
    return [v["id"] for g in r.json()["items"] for v in g["variants"]]


def test_recommendations_require_auth(client):
    r = client.get("/api/v1/recommendations?source_variant_id=1")
    assert r.status_code == 401


def test_recommendations_by_source(client, client_headers):
    _ensure_embeddings()
    ids = _variant_ids(client, client_headers)
    assert ids, "se espera al menos una variante en el catálogo"
    source = ids[0]

    r = client.get(
        f"/api/v1/recommendations?source_variant_id={source}&limit=5",
        headers=client_headers,
    )
    assert r.status_code == 200, r.text
    recs = r.json()
    assert recs, "solo funciona si hay embeddings y otra variante que recomendar"
    assert all(r != source for r in [x["suggested_variant_id"] for x in recs])
    assert all(x["score"] > 0 for x in recs)
    assert all(x["garment_id"] for x in recs)


def test_recommendations_from_browsing_history(client, client_headers):
    _ensure_embeddings()
    ids = _variant_ids(client, client_headers)
    source = ids[0]

    r = client.post(f"/api/v1/recommendations/view/{source}", headers=client_headers)
    assert r.status_code == 200, r.text

    r = client.get("/api/v1/recommendations?limit=5", headers=client_headers)
    assert r.status_code == 200, r.text
    assert r.json()
