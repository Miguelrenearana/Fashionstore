from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.user import Client
from app.schemas.recommendation import RecommendationRead
from app.services.ai_service import ai_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _client_id(db, user) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise NotFoundError("Client profile not found for user.")
    return client.id


@router.get("", response_model=list[RecommendationRead])
def recommend(db: DbSession, current: CurrentUser, source_variant_id: int | None = None, limit: int = Query(10, ge=1, le=50)):
    client_id = _client_id(db, current)
    recs = ai_service.recommend_for_client(db, client_id, source_variant_id, limit)
    result = []
    for rec in recs:
        variant = rec.suggested_variant
        item = RecommendationRead(
            id=rec.id,
            source_variant_id=rec.source_variant_id,
            suggested_variant_id=rec.suggested_variant_id,
            score=float(rec.score),
            variant_name=variant.garment.name if variant else None,
            variant_sku=variant.sku if variant else None,
            garment_id=variant.garment_id if variant else None,
        )
        result.append(item)
    return result


@router.post("/view/{variant_id}")
def log_view(db: DbSession, variant_id: int, current: CurrentUser):
    client_id = _client_id(db, current)
    ai_service.log_view(db, client_id, variant_id)
    return {"ok": True}
