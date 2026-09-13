
from app.schemas.common import ORMModel


class RecommendationRead(ORMModel):
    id: int
    source_variant_id: int | None
    suggested_variant_id: int
    score: float
    variant_name: str | None = None
    variant_sku: str | None = None
