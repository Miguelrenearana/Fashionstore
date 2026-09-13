from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.ml.embeddings import EmbeddingService
from app.ml.vector_store import VectorStore
from app.models.analytics import BrowsingHistory
from app.models.catalog import Garment, GarmentVariant


class RecommenderService:
    def __init__(self, embeddings: EmbeddingService | None = None):
        self._embeddings = embeddings or EmbeddingService()

    def embed_product(self, variant: GarmentVariant, garment: Garment | None = None) -> list[float]:
        garment = garment or variant.garment
        text = EmbeddingService.product_text(
            garment.name,
            garment.category.name if garment.category else None,
            garment.description,
        )
        return self._embeddings.encode(text).tolist()

    def get_recommendations(
        self, db: Session, source_variant_id: int | None, client_id: int | None, limit: int = 10
    ) -> list[tuple[int, float]]:
        query_text: str | None = None
        source_variant = None
        if source_variant_id:
            source_variant = db.get(GarmentVariant, source_variant_id)
            if not source_variant:
                raise NotFoundError("Source variant not found.")
            query_text = self._build_text(source_variant)
        elif client_id:
            history = (
                db.query(BrowsingHistory)
                .filter(BrowsingHistory.client_id == client_id)
                .order_by(BrowsingHistory.view_count.desc())
                .first()
            )
            if history:
                source_variant = db.get(GarmentVariant, history.variant_id)
                if source_variant:
                    query_text = self._build_text(source_variant)

        exclude = [source_variant_id] if source_variant_id else None
        if query_text:
            vector = self._embeddings.encode(query_text).tolist()
            return VectorStore.recommend(vector, limit=limit, exclude_ids=exclude)
        return []

    def _build_text(self, variant: GarmentVariant) -> str:
        garment = variant.garment
        return EmbeddingService.product_text(
            garment.name,
            garment.category.name if garment.category else None,
            garment.description,
        )
