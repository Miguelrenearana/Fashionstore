from app.core.database import SessionLocal
from app.models.catalog import GarmentVariant
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


def test_recommendations_never_repeat_the_same_garment(client, client_headers):
    """El embedding no distingue tallas, asi que una recomendacion debe ser
    SIEMPRE otra prenda: ofrecer otra talla de la que ya se mira no sirve."""
    _ensure_embeddings()
    ids = _variant_ids(client, client_headers)
    source = ids[0]

    r = client.get(
        f"/api/v1/recommendations?source_variant_id={source}&limit=10",
        headers=client_headers,
    )
    assert r.status_code == 200, r.text
    recs = r.json()
    assert recs, "se esperan recomendaciones de otras prendas"

    source_garment = recs_db_garment(source)
    for rec in recs:
        assert rec["garment_id"] != source_garment, (
            f"recomienda la misma prenda ({rec['garment_id']}) en otra variante"
        )
        assert rec["score"] < 1.0, "similitud 1.0 = misma prenda, no es una recomendacion"

    # Tampoco debe repetir la misma prenda entre las recomendaciones.
    assert len({rec["garment_id"] for rec in recs}) == len(recs)


def recs_db_garment(variant_id: int) -> int:
    db = SessionLocal()
    try:
        return db.get(GarmentVariant, variant_id).garment_id
    finally:
        db.close()
